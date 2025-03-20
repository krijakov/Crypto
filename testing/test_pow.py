#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Tests for baseline Proof-of-Work (PoW) algorithm.

"""
import pytest
import sys
from pathlib import Path
parent_dir = Path.cwd().parent
sys.path.append(str(parent_dir))

from src.blockchain.block import Block, Transaction
from src.blockchain.blockchain import Blockchain
from src.blockchain.network import Network
from src.blockchain.node import Node

def test_inits():
    """Test the initialization of the blockchain and network."""
    criterion = lambda x: x.startswith("00")
    blockchain = Blockchain(criterion)
    network = Network(blockchain)
    
    assert network.blockchain == blockchain
    assert network.criterion == criterion
    assert network.nodes == {}
    assert network.public_keys == {}

def test_add_remove_node():
    """Test adding and removing nodes from the network."""
    criterion = lambda x: x.startswith("00")
    blockchain = Blockchain(criterion)
    network = Network(blockchain)
    
    network.add_node("Alice")
    assert "Alice" in network.nodes
    assert "Alice" in network.public_keys
    
    network.remove_node("Alice")
    assert "Alice" not in network.nodes
    assert "Alice" not in network.public_keys

def test_mine_block_turn_based():
    """Test the turn-based mining of a block."""
    tx = Transaction(sender="Miner Micky", receiver="Miner Moe", amount=100)
    tx2 = Transaction(sender="Miner Mike", receiver="Miner Micky", amount=50)
    tx3 = Transaction(sender="Miner Mikey", receiver="Miner Micky", amount=60)

    our_block = Block(index=0, previous_hash="0", data=[tx, tx2, tx3])

    criterion = lambda x: x.startswith("00")
    blockchain = Blockchain(criterion)
    network = Network(blockchain)

    network.add_node("Miner Micky")
    network.add_node("Miner Moe")
    network.add_node("Miner Mike")
    network.add_node("Miner Mikey")

    lucky_miner = network.mine_block_turn_based(block=our_block, max_attempts_per_node=100)

    assert blockchain.validate_chain(network.public_keys) == True, "Chain validation failed."
    assert blockchain.chain[-1].signed_by == lucky_miner.name, "Block not signed by the lucky miner."
    assert lucky_miner.wallet == 10, "Miner did not receive the mining reward."
    assert criterion(blockchain.chain[-1].hash) == True, "Block does not meet the PoW criteria."
    assert blockchain.chain[-1].finalized == True, "Block is not finalized."

def test_mine_without_miners():
    """Test mining when no nodes are available."""
    tx = Transaction(sender="Alice", receiver="Bob", amount=10)
    block = Block(index=0, previous_hash="0", data=[tx])

    criterion = lambda x: x.startswith("00")
    blockchain = Blockchain(criterion)
    network = Network(blockchain)

    lucky_miner = network.mine_block_turn_based(block=block, max_attempts_per_node=100)
    
    assert lucky_miner is None, "Mining should not be possible without nodes."
    assert len(blockchain.chain) == 1, "Blockchain should not add blocks when no nodes exist."

