import sys
import queue

from collections import defaultdict
from transaction import Transaction
from block import CoinBaseTransaction

class TreeNode:
    def __init__(self, blk, time_stamp, parent, n):
        self.block = blk
        self.time_stamp = time_stamp
        self.parent = parent

        self.depth = 0 # 0 is genesis
        
        # Would initialise empty child list here
        self.children = []

        # Would store the balance until this block for all peers
        self.balance = defaultdict(int)

        # Marks whether this node is a part of private chain or not
        # Default is 0
        self.pvt = 0

        if self.parent != None : # Means non-genesis Tree Node
            self.depth = self.parent.depth + 1
            for idx in range(1, n + 1):
                self.balance[idx] = self.parent.balance[idx]

            # Updating balance based on txns added in current block (block must be validated)
            for txn in self.block.txn_list:
                if isinstance(txn, Transaction):
                    self.balance[txn.sender_ID] -= txn.coins
                    self.balance[txn.receiver_ID] += txn.coins

                elif isinstance(txn, CoinBaseTransaction):
                    self.balance[txn.miner] += txn.coins

                else:
                    sys.stderr.write("Incorrect transaction type entered in transaction list of block\n")
                    sys.exit(1)

    # appending tree node to child list
    def add_child(self, child):
        self.children.append(child)

    # function to mark tree node as private
    def mark_private(self):
        self.pvt = 1

    # function to unmark tree node as private
    def unmark_private(self):
        self.pvt = 0

    def __str__(self):
        if self.parent == None:
            return f"BLOCK : IS geneis block with ID {self.block.block_ID}"
        else:
            return f"BLOCK : This Tree Node block ID {self.block.block_ID} and parent block ID {self.block.parent_ID} and checking {self.parent.block.block_ID == self.block.parent_ID}"

class Tree:
    def __init__(self, root):
        self.root = root

    # This function prints blockchain maintained at current peer (using pre-order traversal)
    def print_pre(self, node, peer_dict, file="output/temp.txt", clr=True):
        if clr:
            with open(file, "w") as f:
                f.write("BLOCK ID,TIME STAMP,PARENT ID,MINER,SLOW,LOW_CPU\n")
                f.flush()
        with open(file, "a") as f:
            f.write(f"{node.block.block_ID},{node.time_stamp},{node.parent.block.block_ID if node.parent!=None else 'NULL'},{node.block.txn_list[0].miner if len(node.block.txn_list)>0 else 0},{peer_dict[node.block.txn_list[0].miner].slow if len(node.block.txn_list)>0 else 0},{peer_dict[node.block.txn_list[0].miner].CPU_low if len(node.block.txn_list)>0 else 0}\n")
            f.flush()
            for child in node.children:
                self.print_pre(child, peer_dict, file, False)
    
    # This function prints blockchain maintained at current peer (using binary search traversal)
    def print_bfs(self, node, peer_dict, file="output/temp.txt", clr=True):
        if clr:
            with open(file, "w") as f:
                f.write("BLOCK ID,TIME STAMP,PARENT ID,MINER,SLOW,LOW_CPU,PRIVATE\n")
                f.flush()
        with open(file, "a") as f:
            f.write(f"{node.block.block_ID},{node.time_stamp},{node.parent.block.block_ID if node.parent!=None else 'NULL'},{node.block.txn_list[0].miner if len(node.block.txn_list)>0 else 0},{peer_dict[node.block.txn_list[0].miner].slow if len(node.block.txn_list)>0 else 0},{peer_dict[node.block.txn_list[0].miner].CPU_low if len(node.block.txn_list)>0 and node.block.txn_list[0].miner > 2 else node.block.txn_list[0].miner+1 if len(node.block.txn_list)>0 else 0},{node.pvt}\n")
            f.flush()
            q = queue.Queue()
            q.put(node)
            while not q.empty():
                curr = q.get()
                for child in curr.children:
                    q.put(child)
                    f.write(f"{child.block.block_ID},{child.time_stamp},{child.parent.block.block_ID if child.parent!=None else 'NULL'},{child.block.txn_list[0].miner if len(child.block.txn_list)>0 else 0},{peer_dict[child.block.txn_list[0].miner].slow if len(child.block.txn_list)>0 else 0},{peer_dict[child.block.txn_list[0].miner].CPU_low if len(child.block.txn_list)>0 and child.block.txn_list[0].miner > 2 else child.block.txn_list[0].miner+1 if len(child.block.txn_list)>0 else 0},{child.pvt}\n")
                    f.flush()