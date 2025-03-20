#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Network of nodes/miners. 
In this single machine implementation, there will be a central manager to reduce the complexity coming with a decentralized network (APIs, P2P communication etc.).

"""

from typing import Dict
from src.blockchain.node import Node
from src.blockchain.blockchain import Blockchain
from src.blockchain.block import Block

MINING_REWARD = 10

class Network:
    def __init__(self, blockchain: Blockchain):
        self.nodes: Dict[str, Node] = {}
        self.public_keys = {}

        self.blockchain = blockchain
        self.criterion = blockchain.criterion

    def add_node(self, name: str):
        node = Node(name=name, blockchain=self.blockchain)
        self.public_keys[name] = node.generate_keys()
        self.nodes.setdefault(name, node) # only add if it does not exist

    def remove_node(self, name: str):
        node = self.nodes.get(name)
        if node:
            del self.nodes[name]
            del self.public_keys[name]

    def mine_block_turn_based(self, block: Block, max_attempts_per_node: int = 500):
        """Nodes take turns trying to mine a block, if one succeeds, the they sign the block and add it to the blockchain."""
        if len(self.nodes) == 0:
            print("No nodes in the network. Add some nodes first.")
            return None
        # Prepare the block for mining and addition to the blockchain:
        block = self.blockchain.mark_for_addition(block)
        print("Starting turn-based mining...")
        while True:
            for name, node in self.nodes.items():
                print(f"{name} is attempting to mine...")
                valid_hash = block.mine(self.criterion, max_iterations=max_attempts_per_node)
                if valid_hash:
                    print(f"{name} successfully mined a block: {valid_hash}")
                    # Add reward for the miner
                    node.wallet += MINING_REWARD
                    print(f"{name} received a mining reward of {MINING_REWARD}")
                    node.sign_block(block)
                    chain_valid = self.blockchain.add_block(block, self.public_keys)
                    return node if chain_valid else None
            print("No node found a valid block. Restarting round...")