import hashlib
import json
from transaction import Transaction


SHA3_256 = hashlib.sha3_256


class Block:
    def __init__(self, prev_block, nonce, hash_, transactions, timestamp):
        if prev_block is None:
            self.block_number = 0
            self.last_hash = "0" * 64
        else:
            self.block_number = prev_block.block_number + 1
            self.last_hash = prev_block.hash
        self.nonce = nonce
        self.hash = hash_
        self.transactions = transactions
        self.timestamp = timestamp
        self.validate()

    def validate(self):
        current_hash = SHA3_256(str(self).encode()).hexdigest()
        if current_hash != self.hash:
            raise ValueError("Block is not valid")
        for transaction in self.transactions:
            transaction.validate()

    def get_dict(self):
        return {
            'number': self.block_number,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.last_hash,
            'last_hash': self.last_hash,
            'data': [str(trans) for trans in self.transactions]
        }

    def __str__(self):
        return json.dumps({
            'number': self.block_number,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'last_hash': self.last_hash,
            'data': [str(trans) for trans in self.transactions]
        })

    @staticmethod
    def load_from_dict(value, prev):
        return Block(
            prev,
            value['nonce'],
            value['hash'],
            [Transaction.load_from_string(trans) for trans in value['data']],
            value['timestamp']
        )
