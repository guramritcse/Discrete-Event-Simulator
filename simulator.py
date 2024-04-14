import random
import queue
import copy
from collections import defaultdict

from attacker import Attacker
from honest import Honest

from peer_link import Peer_Link
from block import Block
from tree import TreeNode

class Simulator:
    def __init__(self, n, z0, z1, zeta1, zeta2, T_tx, I, T_sim, env):
        # Initial parameters
        self.n = n
        self.z0 = z0
        self.z1 = z1
        self.zeta1 = zeta1
        self.zeta2 = zeta2
        self.T_tx = T_tx
        self.env = env
        self.I  = I * 1000 # received in secs and converting it to ms
        self.T_sim = T_sim

        # Initialising Peer Dict
        self.peer_dict = dict()
        print("Simulator constructed")

    # Generating 1 with probability z and 0 otherwise
    def generate_RV(self, z):
        sample = random.random()
        if sample < z:
            return 1
        else:
            return 0

    # Creating peers and adding them in the peer dict of simulator
    # Node 1 and 2 are adversaries with zeta1 and zeta2 percentage of mining power respectively
    # TODO: Find High and Low CPU peers percentage from SIR
    def create_peers(self):
        # This variables counts the number of high CPU miners among honest miners
        cnt_high = 0

        for id in range(1, self.n + 1):
            # As of now setting CPU to be high for adversaries, and it is given that adversaries are fast
            if id == 1:
                self.peer_dict[id] = (Attacker(id, self.zeta1, self.T_tx, self.n, self.env))
            elif id == 2:
                self.peer_dict[id] = (Attacker(id, self.zeta2, self.T_tx, self.n, self.env))
            else:
                self.peer_dict[id] = (Honest(id, self.generate_RV(self.z0 / 100.0), self.generate_RV(self.z1 / 100.0), self.T_tx, self.n, self.env))
                if self.peer_dict[id].CPU_low == 0:
                    cnt_high += 1

        # Note, since attacker 1 and 2 combined use up zeta1/100 + zeta2/100 fraction of hashing power,
        # Remaining nodes needs to distribute the remaining hashing fraction among them based on number of
        # high and low cpu power in honest miners
        h = (1.0 - ((self.zeta1 / 100.0) + (self.zeta2/100.0))) / (9.0*cnt_high + self.n - 2)
        slow_mine_time = self.I / h

        # hashing power fraction set for all peers
        # Mean block inter-arrival time being set for adversaries
        if self.zeta1 != 0:
            self.peer_dict[1].update_block_mine_time(self.I / (self.zeta1 / 100.0))
        if self.zeta2 != 0:
            self.peer_dict[2].update_block_mine_time(self.I / (self.zeta2 / 100.0))

        # id's range is starting from 3 cause 1 and 2 are adversaries
        for id in range(3, self.n + 1):
            if self.peer_dict[id].CPU_low: # if CPU is low
                self.peer_dict[id].update_block_mine_time(slow_mine_time)
            else:
                self.peer_dict[id].update_block_mine_time(slow_mine_time / 10.0)
        
        # Added genesis block and its tree node to all the peers
        genesis_blk = Block(0, None, 1000)

        # Emptying the txn_list cause by default it adds coin base txn for the miner
        genesis_blk.txn_list = []

        # Generating corresponding tree node for the genesis block
        genesis_tree_node = TreeNode(genesis_blk, self.env.now, None, self.n)
        for id in range(1, self.n + 1):
            self.peer_dict[id].add_genesis_block(copy.deepcopy(genesis_tree_node))


    # This function checks if given edge list representation forms a connected graph or not
    def check_connectivity(self, edge_list):
        visited = [0] * self.n

        # Initialsing queue to do BFS
        q = queue.Queue(maxsize = 0)

        # Starting arbitrarily with node '0'
        # Note, edge list is 1 indexed whereas here q and visited are 0 indexed
        q.put(0)

        # Main BFS algo 
        while(not q.empty()):
            # Getting the element from queue
            elem = q.get()

            # Continuing if already visited
            if visited[elem]:
                continue

            # Else, marking current elem as visited
            visited[elem] = 1

            # Adding unvisited neighbors of current elem to q
            for nxt in edge_list[elem + 1]:
                if visited[nxt-1] == 0:
                    q.put(nxt-1)
        
        return (sum(visited) == self.n)

    # Making connected graph for the nodes
    def create_network_graph(self, min_peers, max_peers):
        # Initialising empty edge list for the network graph
        edge_list = defaultdict(list)

        # Variable that on 1 denotes if connected graph is obtained or not, 0 otherwise
        grph_made = 0

        # Continue attempting to make graph until connectivity is achieved
        while(grph_made == 0):
            # Emptying edge_list of previous failed attempts
            edge_list.clear()

            # This stores initially how many neighbour nodes to connect for each node
            p_cnt = dict()

            # Populating the p_cnt, with values between min_peers and max_peers (both inclusive)
            for idx in range(1, self.n+1):
                # How many nodes is the current node connected to?
                peer_cnt = random.randint(min_peers, max_peers)
                peer_cnt = min(peer_cnt, self.n - 1)
                p_cnt[idx] = peer_cnt
            
            # This loop tries to create graph, crct_ngb variable if 1 says for loop 
            # executed successfully by giving each node required number or neighbors
            # and is 0 otherwise
            crct_ngb = 1
            for idx in range(1,self.n+1):
                # This tm is for a heuristic such that we attempt to allocate a neighbor
                # within only n^2 tries, this helps in us not getting stuck in an infinte 
                # while loop (Eg, all nodes have been connected to required number of neighbors
                # but not say node x, then any candidate neighbor would be rejected and we would be
                # stuck in a while loop)
                tm = 0

                # Note p_cnt[idx], actually store number of neighbors yet needed to be connected
                # for a node idx and hence it dynamically reduces by 1 on each successful connection
                # Until no more neighbors are required (i.e., p_cnt[idx] == 0)
                while(p_cnt[idx] > 0 and tm < self.n*self.n):
                    tm += 1

                    # ngb is candidate neighbor
                    ngb = random.randint(1, self.n)

                    # Only add ngb as peer to current node, if peer not same as current node,
                    # peer still has connecting capacity left (i.e., p_cnt[ngb] > 0) and peer
                    # not already a neighbor of current node
                    if (ngb != idx) and (p_cnt[ngb] > 0) and (ngb not in edge_list[idx]):
                        edge_list[idx].append(ngb)
                        p_cnt[idx] -= 1

                        edge_list[ngb].append(idx)
                        p_cnt[ngb] -= 1

                # On incorrect exit of while loop, attempt again
                if p_cnt[idx] != 0:
                    crct_ngb = 0
                    break
            if not crct_ngb :
                continue
            
            
            # Checking if graph is connected
            grph_made = self.check_connectivity(edge_list)
        print("Graph made successfully")
        # print(edge_list)
        return edge_list

    # This function would actually materialise the connections of the p2p network
    def create_p2p_links(self, edge_list):
        for idx in range(1, self.n+1):
            for ngb in edge_list[idx]:
                lnk = Peer_Link(self.peer_dict[idx], self.peer_dict[ngb], self.env)
                self.peer_dict[idx].update_send_list(lnk)

    def my_timer(self):
        while True:
            print("Current time is :", self.env.now)
            yield self.env.timeout(100)
    
    def start_simulation(self):
        print("Creating p2p network")
        # Initialising nodes of the network
        self.create_peers()

        # Generating network topology
        edge_list = self.create_network_graph(3,6)

        # Create actual peer links based on topology
        self.create_p2p_links(edge_list)
        
        for idx in range(1, self.n+1):
            self.env.process((self.peer_dict[idx]).txn_sender())
            self.env.process((self.peer_dict[idx]).reader())

        self.env.process((self.peer_dict[1]).create_pvt_block())
        self.env.process((self.peer_dict[2]).create_pvt_block())
        for idx in range(3, self.n+1):
            # It starts the intial block formation at each peer
            self.env.process((self.peer_dict[idx]).create_and_transmit_new_block())

        self.env.process(self.my_timer())

    # This function would print the blockchain of all the peers
    def print_blockchain(self, output_dir):
        print(f"Printing blockchain")
        for idx in range(1, self.n+1):
            self.peer_dict[idx].print_blockchain(self.peer_dict, output_dir)

    # This function would generate info about minors, simulation's parameters and write it to a file
    def generate_info(self, file):
        # print(f"Writing simulation's parameters")
        with open(file, "w") as f:
            f.write(f"Simulation time (in s): {self.T_sim}\n")
            f.write(f"Number of peers in the network (n): {self.n}\n")
            f.write(f"Percentage of honest slow peers (z0): {self.z0}\n")
            f.write(f"Percentage of honest peers with low CPU (z1): {self.z1}\n")
            f.write(f"Percentage of mining power of adversary-1 (zeta1): {self.zeta1}\n")
            f.write(f"Percentage of mining power of adversary-2 (zeta2): {self.zeta2}\n")
            f.write(f"Mean interarrival time between transactions (in ms) (T_tx): {self.T_tx}\n")
            f.write(f"Mean interarrival time between blocks (in ms) (I): {self.I}\n")
            f.write("==============================================\n")
            f.flush()
            print(f"Generating miner info")
            f.write("ID,Slow|Fast,Low CPU|High CPU\n")
            f.write(f'1,Fast,Attacker 1\n')
            f.write(f'2,Fast,Attacker 2\n')
            for idx in range(3, self.n+1):
                f.write(f'{idx},{"Slow" if self.peer_dict[idx].slow else "Fast"},{"Low CPU" if self.peer_dict[idx].CPU_low else "High CPU"}\n')
                f.flush()