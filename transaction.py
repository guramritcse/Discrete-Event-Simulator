class Transaction:
    def __init__(self, sender_ID, receiver_ID, coins, txn_ID, txn_size):
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID
        self.coins = coins
        self.txn_ID = txn_ID
        self.curr_sender = sender_ID
        self.txn_size = txn_size # It is in KB

    def __str__(self):
        return f"{self.txn_ID}: {self.sender_ID} pays {self.receiver_ID} {self.coins} coins"