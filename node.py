import calendar
import hashlib
import json
import time
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

SHA3_256 = hashlib.sha3_256


class Transaction:
    def __init__(self, from_, to, value):
        self.from_ = from_
        self.to = to
        self.value = value
        self.signature = None

    def set_signature(self, signature):
        self.signature = signature
        self._valid_from()

    def validate(self):
        self._valid_from()

    def _valid_from(self):
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), bytes.fromhex(self.from_))
        public_key.verify(bytes.fromhex(self.signature), self.get_data(), ec.ECDSA(hashes.SHA3_256()))

    def get_data(self):
        return f"{self.from_};{self.to};{self.value}".encode()

    def __str__(self):
        return f"{self.from_};{self.to};{self.value};{self.signature}"

    @staticmethod
    def load_from_string(value):
        [from_, to, value, signature] = value.split(';')
        trans = Transaction(from_, to, value)
        trans.set_signature(signature)
        return trans


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


class BlockChain:
    def __init__(self):
        self.blocks = []
        self.pending_transactions = []
        self.add_genesis_block()

    def add_genesis_block(self):
        print("Start generating genesis block...")
        block = Miner(None, [], calendar.timegm(time.gmtime())).get_block()
        self._append_block(block)
        print("Genesis block mined.")

    def _append_block(self, block):
        self.blocks.append(block)

    def add_transaction(self, transaction):
        print("Transaction added:")
        print(f"   > from = {transaction.from_}")
        print(f"   > to = {transaction.to}")
        print(f"   > amount = {transaction.value}")
        print(f"   > proof = {transaction.signature}")
        self.pending_transactions.append(transaction)
        if len(self.pending_transactions) >= 2:
            self.generate_new_block()

    def generate_new_block(self):
        if len(self.pending_transactions) <= 1:
            return
        print()
        print("Start generating new block...")
        new_transactions = self.pending_transactions[:2]
        self.pending_transactions = self.pending_transactions[2:]
        block = Miner(self.blocks[-1], new_transactions, calendar.timegm(time.gmtime())).get_block()
        self._append_block(block)
        print("New block mined.")
        if len(self.pending_transactions) >= 2:
            self.generate_new_block()

    def _parse_chain(self):
        parsed_chain = [block.get_dict() for block in self.blocks]
        return parsed_chain

    @staticmethod
    def load_chain(blocks):
        new_chain = [Block.load_from_dict(blocks[0], None)]
        for block_index in range(len(blocks[1:])):
            new_chain.append(Block.load_from_dict(blocks[block_index], new_chain[block_index - 1]))
        return new_chain

    @staticmethod
    def validate_blocks(blocks):
        last_number = 0
        last_timestamp = 0
        last_hash = ""
        for block in blocks:
            block.validate()
            block.block_number = last_number
            if block.timestamp < last_timestamp:
                raise ValueError()
            if block.block_number != 0 and block.last_hash == last_hash:
                raise ValueError()
            last_number += 1
            last_timestamp = block.timestamp
            last_hash = block.hash


def get_new_transaction(to, amount):
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint
    )
    address = pem.hex()
    transaction = Transaction(address, to, amount)
    signature = private_key.sign(
        transaction.get_data(),
        ec.ECDSA(hashes.SHA3_256())
    ).hex()
    transaction.set_signature(signature)
    return transaction


if __name__ == '__main__':
    print("Starting blockchain...")
    blockchain = BlockChain()
    print("Blockchain started.")

    print()
    # Add transaction 1
    blockchain.add_transaction(
        get_new_transaction(
            "034cf36df4c62283c86d4376a2565686ed7bc8bab8f3b59cf0d8d7013028e354d8",
            0.11123
        )
    )

    print()
    # Add transaction 2
    blockchain.add_transaction(
        get_new_transaction(
            "029841a0f8c4e34e273e58fb42114cae3fd57c1def6b1423623bfa83803ab94803",
            0.85521
        )
    )

    print()
    # Add transaction 3
    blockchain.add_transaction(
        get_new_transaction(
            "0333205be4438053a5c8feb91b9dd899c2d7d846a03e3ce581b98b2ddb662c6fc2",
            0.9638
        )
    )

    print()
    # Add transaction 4
    blockchain.add_transaction(
        get_new_transaction(
            "038358985dd9e7b6adc73f7129cd1daff32fb730ccc08a0ee0eb238f5fdc2c0ded",
            2.21312
        )
    )

