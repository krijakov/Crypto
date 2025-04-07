#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Node/miner in the blockchain network.

"""
import random

from app.blockchain.blockchain import Blockchain
from app.blockchain.block import Transaction, Block
from app.blockchain.digital_signature.ecc import ECC, secp256k1


class Node:
    def __init__(self, name: str, blockchain: Blockchain):
        self.name = name
        self.blockchain = blockchain

        self.wallet = 0 # Initial balance

        self._private_key = None # NOTE: make this private
        self._public_key = None

    @property
    def public_key(self):
        return self._public_key
    
    def generate_keys(self, curve: ECC = secp256k1):
        """Generate a new key pair."""
        self._private_key = random.randint(1, curve.n - 1)
        self._public_key = curve.scalar_multiply(self._private_key, curve.G)
        return self._public_key
    
    # Auxiliary functions:
    def get_balance(self) -> int:
        """Get the balance of the node."""
        return self.wallet
    
    def get_available_nodes(self, network):
        """Get the available nodes in the network."""
        return network.nodes.keys()

    # Atomic Actions:

    def submit_transaction(self, receiver: str, amount: int) -> Transaction:
        """Submit a transaction to the network."""
        assert amount > 0, "Transaction amount must be positive."
        assert self.wallet >= amount, "Insufficient balance."
        assert receiver in self.get_available_nodes(), "Receiver not available in the network."
        transaction = Transaction(sender=self.name, receiver=receiver, amount=amount)
        transaction.sign(self._private_key)
        self.wallet -= amount
        return transaction

    def attempt_mining(self):
        ...


    # Mining/Validation:

    def sign_transaction(self, transaction: Transaction):
        """Sign the transaction."""
        if not self._private_key:
            raise ValueError("Private key not generated. Call generate_keys() first.")
        transaction.sign(self._private_key)

    def sign_block(self, block: Block):
        """Sign the block."""
        for tx in block.data:
            self.sign_transaction(tx)
        block.is_signed = True
        block.signed_by = self.name
    
    def validate(self) -> bool:  
        """Check is the blockchain is valid."""
        return self.blockchain.validate_chain()   
    

        