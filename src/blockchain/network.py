#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Network of nodes/miners. 
In this single machine implementation, there will be a central manager to reduce the complexity coming with a decentralized network (APIs, P2P communication etc.).

"""

from typing import Dict
from src.blockchain.node import Node
from src.blockchain.blockchain import Blockchain

class Network:
    def __init__(self, blockchain: Blockchain):
        self.nodes: Dict[str, Node] = {}
        self.blockchain = blockchain
        self.criterion = blockchain.criterion

    def add_node(self, name: str):
        node = Node(name=name, blockchain=self.blockchain)
        self.nodes.setdefault(name, node) # only add if it does not exist

    def remove_node(self, name: str):
        node = self.nodes.get(name)
        if node:
            del self.nodes[name]

    def mine_block_turn_based(self, data: str, max_attempts_per_node: int = 500):
        """Let each node mine a block in turn."""
        print("Starting turn-based mining...")
        while True:
            for name, node in self.nodes.items():
                print(f"{name} is attempting to mine...")
                block_hash = node.mine_block(data=data, max_iterations=max_attempts_per_node)
                if block_hash:
                    print(f"{name} successfully mined a block: {block_hash}")
                    return block_hash
            print("No node found a valid block. Restarting round...")
