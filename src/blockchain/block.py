#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Single block from the blockchain.

"""
from src.hashing.sha2 import SHA256
from datetime import datetime
from typing import Callable, Optional

class Block:
    __slots__ = ("_index", "_previous_hash", "_data", "_timestamp", "_nonce", "_hash")
    
    def __init__(self, index: int, previous_hash: str, data: str, timestamp: datetime.timestamp = None, nonce: int = 0):
        self._index = index
        self._previous_hash = previous_hash
        self._data = data
        self._timestamp = timestamp if timestamp is not None else datetime.now().timestamp()
        self._nonce = nonce
        self._hash = SHA256.digest(f"{self._previous_hash}{self._timestamp}{self._data}{self._nonce}")
           
    @property
    def index(self) -> int:
        return self._index
    
    @property
    def previous_hash(self) -> str:
        return self._previous_hash
    
    @property
    def data(self) -> str:
        return self._data
    
    @property
    def timestamp(self) -> datetime.timestamp:
        return self._timestamp
    
    @property
    def nonce(self) -> int:
        return self._nonce
    
    @nonce.setter
    def nonce(self, value: int):
        self._nonce = value
        self._hash = SHA256.digest(f"{self._previous_hash}{self._timestamp}{self._data}{self._nonce}")
    
    @property
    def hash(self) -> str:
        return self._hash
    
    # Proof of Work:
    def mine(self, criteria: Callable[[str], bool], max_iterations: int = 1000) -> Optional[str]:
        """Perform Proof-of-Work until the criteria is met or max iterations is reached."""
        while not criteria(self._hash):
            if self._nonce > max_iterations:
                return None # this might need refinement, assumes the nonce always starts at 0
            self.nonce += 1 # this should update the hash through the setter for nonce
        return self._hash