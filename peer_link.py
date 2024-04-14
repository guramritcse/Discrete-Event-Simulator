import random 
import numpy as np

from block import Block
from transaction import Transaction

class Peer_Link :
    def __init__(self, sender, receiver, env):
        self.sender = sender
        self.receiver = receiver
        self.env = env

        # Finding the transmission delay params
        self.p_ij = random.uniform(10, 500) # It's in ms
        self.c_ij = 100 # It's in Mbps
        if (sender.slow or receiver.slow) :
            self.c_ij = 5
        self.d_ij_mean = (96.0/self.c_ij)   # It's in ms

    def send_txn(self, txn): # txn_size is in KB (default is 1KB)
        def per_msg_sender():
            d_ij = np.random.exponential(scale=(self.d_ij_mean))

            # delay in ms, factor of 8 is to convert bytes to bits
            delay = self.p_ij + ((txn.txn_size * 8.0)/self.c_ij) + d_ij

            # if isinstance(txn, Block):
            #     print(f"BLOCK: Delay of {self.sender.ID} to {self.receiver.ID} is {delay} ++++++ TIME {self.env.now}")
            # if isinstance(txn, Transaction):
            #     print(f"TXN: Delay of {self.sender.ID} to {self.receiver.ID} is {delay} ++++++ TIME {self.env.now}")

            yield self.env.timeout(delay) # time is in milliseconds

            # Sending transaction by adding it to receiver's queue
            self.receiver.read_queue.put(txn)
            
        self.env.process(per_msg_sender())
        
