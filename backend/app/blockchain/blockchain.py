#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The main blockchain class.

"""
import json

from typing import List, Callable
from models.mining_criterion import MiningCriterion
from blockchain.block import Block
from configs import logger

class Blockchain:
    def __init__(self, criterion: MiningCriterion):
        self.chain: List[Block] = []
        self.criterion = criterion

        self.create_genesis_block()

    def load_from_json(self, json_path):
        with open(json_path, "r", encoding='utf-8') as bf:
            chain_dict = json.load(bf)

        self.chain = [Block.load_from_dict(d) for d in chain_dict.get("blocks")]

    def create_genesis_block(self):
        self.chain.append(Block(index=0, previous_hash="0", data=[], criterion=self.criterion)) # Genesis block

    def validate_chain(self) -> bool:
        """Validate the entire chain's integrity and Proof-of-Work."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
    
            # Check previous hash linkage
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Invalid hash linkage at block {current_block.index}")
                return False
            
            # Recompute the hash to validate PoW
            if current_block.compute_hash() != current_block.hash:
                logger.error(f"Invalid PoW at block {current_block.index}")
                return False
    
        return True
    
    def add_block(self, block: Block) -> bool:
        """Add a block to the blockchain."""
        self.chain.append(block)
        if not self.validate_chain():
            self.chain.pop(-1)
            return False
        return True
    
    def json_serialize(self):
        return {
            "blocks": [b.json_serialize() for b in self.chain]
        }

