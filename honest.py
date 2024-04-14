from peer import Peer
from tree import TreeNode

class Honest(Peer):
    def __init__(self, ID, slow, CPU_low, T_tx, n, env):
        super().__init__(ID, slow, T_tx, n, env)
        self.CPU_low = CPU_low

    def block_receiver(self, blk):
        if not self.validate_block(blk):
            return

        # Since block is validated, forward it to others
        # Sending the block to all the connected peers only if not an adversary or if an adversary, then block is of the adversary
        # Need to create tree node and add the mapping to block_to_tree
        self.block_to_tree[blk.block_ID] = TreeNode(blk, self.env.now, self.block_to_tree[blk.parent_ID], self.n)

        # Adding as child, current block in the parent block's node
        self.block_to_tree[blk.parent_ID].add_child(self.block_to_tree[blk.block_ID])

        # Putting buffered blocks(if any) whose parent is this block back in read queue with 0 delay
        if blk.block_ID in self.buffer_blocks.keys(): 
            for a in self.buffer_blocks[blk.block_ID]:
                self.read_queue.put(a)
            del self.buffer_blocks[blk.block_ID]
        self.forward_block(blk) 

        # Does it create a new longest chain
        if self.block_to_tree[blk.block_ID].depth > self.curr_tree_node.depth :
            # print(f"BLOCK: Curr tree node changed {self.ID}")
            # If yes, select subset of txns received so far not included in any blocks in the longest chain
            # Generate Tk = I/hk
            self.curr_tree_node = self.block_to_tree[blk.block_ID]

            # Launching this as process so that reader doesn't time out during 
            # block PoW mining
            self.env.process(self.create_and_transmit_new_block())