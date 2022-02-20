import calendar
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from block import Block
from miner import Miner
from transaction import Transaction


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
