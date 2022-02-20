from blockchain import BlockChain, get_new_transaction

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