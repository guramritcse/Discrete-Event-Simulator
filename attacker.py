from peer import Peer
from tree import TreeNode
from block import Block
import copy
import numpy as np

class Attacker(Peer):
    def __init__(self, ID, zeta, T_tx, n, env):
        super().__init__(ID, 0, T_tx, n, env)
        self.zeta = zeta
        self.pvt_chain = []
        self.lead = 0

    # start making pvt block having parent as curr_tree_node
    def create_pvt_block(self, parent_node = None):
        # If attacker's hashing fraction is 0 don't create blocks
        if self.zeta == 0:
            return

        if(parent_node == None):
            parent_node = self.curr_tree_node
        
        # New block created
        new_block = Block(self.ID, parent_node.block.block_ID, 1000)

        # This stores balance of each peer as of now
        spending = copy.deepcopy(parent_node.balance)

        for txn in self.txns_seen.values():
            if not self.txn_not_already_present(txn, parent_node):
                continue

            # Can only add this txn if sender's balance is more than what he wants to spend
            if spending[txn.sender_ID] >= txn.coins :
                # O is returned if max limit reached and block not added
                if new_block.add_txn_to_block(txn) == 0: #Not added txn to Block
                    break

                # If 1 received that means, txn added successfully to block, update balance
                spending[txn.sender_ID] -= txn.coins
        
        # now valid transactions have been added to the block
        # Simulating PoW
        to_time = np.random.exponential(scale=(self.block_mine_time))
        # print(f"PRIVATE BLOCK: {self.ID} creation start at {new_block.block_ID} at {self.env.now} TO for {to_time}")
        yield self.env.timeout(to_time)

        # now PoW has been simulated
        # checking if peer has the same longest chain
        # that is curr_tree_node is the same or not
        # now checking block's parent ID is same as cur_tree_node.block_ID
        if new_block.parent_ID == self.curr_tree_node.block.block_ID:
            # print(f"11 PRIVATE BLOCK: {self.ID} longest so adding to self read queue {new_block.block_ID} at {self.env.now}")
            # add this block in my tree
            # self.block_receiver(new_block)
            # Adding this to my own read_queue cause now we need to add it to our block chain
            self.read_queue.put(new_block)
        elif len(self.pvt_chain) != 0 and new_block.parent_ID == self.pvt_chain[-1].block.block_ID:
            # print(f"22 PRIVATE BLOCK: {self.ID} longest so adding to self read queue {new_block.block_ID} at {self.env.now}")
            self.read_queue.put(new_block)
        # else: 
            # print(f"PRIVATE BLOCK: {self.ID} && {new_block.block_ID} at {self.env.now} Rejected ")

    # should transmit and delete block from pvt chain
    def transmit_pvt_block(self):
        # Not only transmit but also mark the treenode pas not private
        self.pvt_chain[0].unmark_private()
        del_node = self.pvt_chain.pop(0)
        self.forward_block(del_node.block)
    
    def block_receiver(self, blk):
        if not self.validate_block(blk):
            return

        # Now we mark the block received as seen
        # Need to create tree node and add the mapping to block_to_tree
        self.block_to_tree[blk.block_ID] = TreeNode(blk, self.env.now, self.block_to_tree[blk.parent_ID], self.n)

        # Adding as child, current block in the parent block's node
        self.block_to_tree[blk.parent_ID].add_child(self.block_to_tree[blk.block_ID])

        # Putting buffered blocks(if any) whose parent is this block back in read queue with 0 delay
        if blk.block_ID in self.buffer_blocks.keys(): 
            for a in self.buffer_blocks[blk.block_ID]:
                self.read_queue.put(a)
            del self.buffer_blocks[blk.block_ID]

        ###################################
        if blk.txn_list[0].miner != self.ID:
            # print(f"BLOCK {blk.block_ID} IS MINED BY HONEST, FOUND AT SELFISH : {self.ID}")
            # print(f"Current state at attacker {self.ID}  is {self.lead}")
            # Does it create a new longest chain
            if self.block_to_tree[blk.block_ID].depth <= self.curr_tree_node.depth :
                # print(f"BLOCK {blk.block_ID} at {self.ID} DIDN'T DO AMYTHING CAUSE WAS NOT AT MAX DEPTH")
                return
            else:
                # lead as -1 is state O dash
                if self.lead == -1 or self.lead == 0:
                    # print(f"BLOCK {blk.block_ID} at {self.ID} BECAME NEW CURRENT NODE")
                    self.curr_tree_node = self.block_to_tree[blk.block_ID]
                    self.env.process(self.create_pvt_block())
                    self.lead = 0
                
                elif self.lead == 1:
                    # print(f"BLOCK {blk.block_ID} at {self.ID} INITIATED RELEASE OF BLOCK {self.pvt_chain[-1].block.block_ID} FROM PVT CHAIN")
                    self.curr_tree_node = self.block_to_tree[self.pvt_chain[-1].block.block_ID]
                    self.transmit_pvt_block()
                    self.lead = -1
                
                elif self.lead == 2:
                    # print(f"BLOCK {blk.block_ID} at {self.ID} INITIATED RELEASE OF BLOCKS {self.pvt_chain[-1].block.block_ID} and {self.pvt_chain[-2].block.block_ID} FROM PVT CHAIN")
                    self.curr_tree_node = self.block_to_tree[self.pvt_chain[-1].block.block_ID]
                    self.transmit_pvt_block()
                    self.transmit_pvt_block()
                    self.lead = 0

                else :
                    # print(f"BLOCK {blk.block_ID} at {self.ID} INITIATED RELEASE OF BLOCKS {self.pvt_chain[-1].block.block_ID} FROM PVT CHAIN lead decreased by 1")
                    self.lead = self.lead - 1
                    self.curr_tree_node = self.block_to_tree[self.pvt_chain[0].block.block_ID]
                    self.transmit_pvt_block()
        else:
            # print(f"BLOCK {blk.block_ID} IS MINED AND RECEIVED AT SELFISH : {self.ID}")
            # print(f"Current state at attacker {self.ID}  is {self.lead}")
            self.pvt_chain.append(self.block_to_tree[blk.block_ID])
            # Marking the node as private
            self.pvt_chain[-1].mark_private()
            if self.lead == -1:
                # print(f"BLOCK {blk.block_ID} at {self.ID} INITITATED RELEASE OF BLOCK {self.pvt_chain[-1].block.block_ID} FROM PVT CHAIN")
                self.curr_tree_node = self.block_to_tree[self.pvt_chain[-1].block.block_ID]
                self.transmit_pvt_block()
                self.lead = 0
                self.env.process(self.create_pvt_block())
            else:
                # print(f"BLOCK {blk.block_ID} at {self.ID} BECAME PART OF PVT CHAIN")
                self.lead = self.lead + 1
                self.env.process(self.create_pvt_block(self.pvt_chain[-1]))