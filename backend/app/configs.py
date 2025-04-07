#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Configuration handling for the app.

"""
from dataclasses import dataclass
import logging
import sys
from pathlib import Path

cwd = Path.cwd()

@dataclass
class Configs:
    MINING_REWARD: int = 10
    BLOCKCHAIN_LOCATION: str = str(cwd / "blockchain/BLOCKCHAIN.json")
    PENDING_TRANSACTIONS: int = 1
    MINING_TYPE: str = "leading_zeros"
    MINING_DIFFICULTY: int = 3

configs = Configs()

def get_configs():
    return configs

# Create a simple logger:
logger = logging.getLogger("Blockchain logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_logger():
    return logger
