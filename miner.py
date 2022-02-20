import hashlib
import json
import sys
from block import Block


SHA3_256 = hashlib.sha3_256


class Miner:
    def __init__(self, prev_block, transactions, timestamp):
        self.prev_block = prev_block
        self.transactions = transactions
        self.timestamp = timestamp

    def get_block(self):
        nonce = 0
        block_number = 0
        last_hash = "0" * 64
        if self.prev_block is not None:
            block_number = self.prev_block.block_number + 1
            last_hash = self.prev_block.hash
        while True:
            raw_block = json.dumps({
                'number': block_number,
                'timestamp': self.timestamp,
                'nonce': nonce,
                'last_hash': last_hash,
                'data': [str(trans) for trans in self.transactions]
            })
            gen_hash = SHA3_256(raw_block.encode()).hexdigest()
            sys.stdout.write("\rLooking for nonce, current: %i" % nonce)
            sys.stdout.flush()
            if gen_hash.startswith("0f0f"):
                print()
                return Block(self.prev_block, nonce, gen_hash, self.transactions, self.timestamp)
            nonce += 1
