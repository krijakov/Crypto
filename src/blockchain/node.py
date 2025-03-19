#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Node/miner in the blockchain network.

"""
import random

from src.blockchain.blockchain import Blockchain
from src.blockchain.block import Transaction, Block
from digital_signature.ecc import ECC, secp256k1


class Node:
    def __init__(self, name: str, blockchain: Blockchain):
        self.name = name
        self.blockchain = blockchain

        self._private_key = None
        self._public_key = None

    @property
    def public_key(self):
        return self._public_key
    
    def generate_keys(self, curve: ECC = secp256k1):
        """Generate a new key pair."""
        self._private_key = random.randint(1, curve.n - 1)
        self._public_key = curve.scalar_multiply(self._private_key, curve.G)
       
    def mine_block(self, data: Transaction, max_iterations: int = 1000 ) -> str:
        """Mine and add a block to the blockchain with the given data."""
        block = self.blockchain.add_block_PoW(data, max_iterations=max_iterations)
        return block
    
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
        