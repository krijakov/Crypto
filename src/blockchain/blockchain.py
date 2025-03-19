#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The main blockchain class.

"""

from typing import List, Optional, Callable
from src.blockchain.block import Block, Transaction

class Blockchain:
    def __init__(self, criterion: Callable[[str], bool]):
        self.chain: List[Block] = []
        self.criterion = criterion

        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append(Block(index=0, previous_hash="0", data=[])) # Genesis block


    def add_block_PoW(self, data: List[Transaction], max_iterations: int = 1000) -> Optional[Block]:
        """Add a block to the blockchain using Poof-of-Work."""
        previous_block = self.chain[-1]
        new_block = Block(index=previous_block.index + 1, previous_hash=previous_block.hash, data=data)
    
        # Validate the new block using PoW:
        mined_hash = new_block.mine(self.critertion, max_iterations=max_iterations)
        if mined_hash:
            self.chain.append(new_block)
            return new_block
        return None
    
    def validate_chain(self) -> bool:
        """Validate the entire chain's integrity and Proof-of-Work."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
    
            # Check previous hash linkage
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Recompute the hash to validate PoW
            if current_block.compute_hash() != current_block.hash:
                return False
    
        return True

