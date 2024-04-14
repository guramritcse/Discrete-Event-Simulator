import random
import hashlib
import datetime

class CoinBaseTransaction:
    def __init__(self, miner, txn_size = 1, coins = 50):
        self.miner = miner
        self.txn_size = txn_size
        self.coins = coins

        # Would make txn_ID
        # Generating unique transaction ID here
        txn_data = f"{self.miner} mines {self.coins} coins" + str(random.randint(1, 10000000000)) + "___" + str(random.randint(1, 10000000000))+ str(datetime.datetime.now().microsecond)
        self.txn_ID = hashlib.sha256(txn_data.encode()).hexdigest()

    def __str__(self):
        return f"{self.txn_ID}: {self.miner} mines {self.coins} coins"


class Block:
    def __init__(self, miner, parent_ID, mx_block_size = 1000):
        self.mx_block_size = mx_block_size # It is in KB
        self.parent_ID = parent_ID
        self.txn_size = 1 # for coinbase transaction

        # Initialsing txn list with coin base txn
        self.txn_list = [CoinBaseTransaction(miner, 1, 50)]

        # Assigning block ID
        blk_data = f"{miner}" + str(random.randint(1, 10000000000)) + "$$$" + str(random.randint(1, 10000000000)) + str(datetime.datetime.now().microsecond)
        self.block_ID = hashlib.sha256(blk_data.encode()).hexdigest()

        # Storing the sender through which peer receieved this block, by default
        # miner would have created this block and hence is a sender
        self.curr_sender = miner

    def get_blk_size(self):
        return len(self.txn_list)

    # returns 1 if transaction added to block, else 0
    def add_txn_to_block(self, txn):
        if self.get_blk_size() < self.mx_block_size:
            self.txn_list.append(txn)

            #increment block size
            self.txn_size += 1
            return 1
        return 0
    
    def __str__(self):
        return f"Block with ID {self.block_ID} mined by {self.txn_list[0].miner}"