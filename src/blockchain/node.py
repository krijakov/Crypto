#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Node/miner in the blockchain network.

"""
from typing import Callable

from src.blockchain.block import Block


class Node:
    def __init__(self, name: str):
        self.name = name
        
    def mine(self, block: Block, criteria: Callable[[str], bool]) -> Block:
        """Mine a block until the criteria is met."""
        block_hash = block.mine(criteria, max_iterations=1000) # this might need refinement, assumes the nonce always starts at 0
        if block_hash:
            return block
        return None
        
    def broadcast(self, block: Block):
        """Broadcast a block to the network."""
        pass
    
    def receive(self, block: Block):
        """Receive a block from the network."""
        pass
    
    def validate(self, block: Block, criteria: Callable[[str], bool]) -> bool:  
        """Validate a block against the criteria."""
        return criteria(block.hash)
    
    
        