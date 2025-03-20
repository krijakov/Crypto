#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The main blockchain class.

"""

from typing import List, Callable, Dict, Tuple
from src.blockchain.block import Block

class Blockchain:
    def __init__(self, criterion: Callable[[str], bool]):
        self.chain: List[Block] = []
        self.criterion = criterion

        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append(Block(index=0, previous_hash="0", data=[])) # Genesis block

    def mark_for_addition(self, block: Block) -> Block:
        """Mark a block for addition to the blockchain."""
        previous_block = self.chain[-1]
        block.index = previous_block.index + 1
        block.previous_hash = previous_block.hash
        block.nonce = 0 # Reset nonce (this also recalculates the hash)
        return block
    
    def validate_chain(self, public_key_registry: Dict[str, Tuple[int, int]]) -> bool:
        """Validate the entire chain's integrity and Proof-of-Work."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
    
            # Check previous hash linkage
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid hash linkage at block {current_block.index}")
                return False
            
            # Recompute the hash to validate PoW
            if current_block.compute_hash() != current_block.hash:
                print(f"Invalid PoW at block {current_block.index}")
                return False
            
            # Verify all transactions in the block
            if not current_block.verify_transactions(public_key_registry):
                print(f"Invalid transactions at block {current_block.index}")
                return False
    
        return True
    
    def add_block(self, block: Block, public_key_registry: Dict[str, Tuple[int, int]]) -> bool:
        """Add a block to the blockchain."""
        self.chain.append(block)
        return self.validate_chain(public_key_registry=public_key_registry)

