#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Single block from the blockchain.

"""
from src.hashing.sha2 import SHA256
from src.digital_signature.ecc import ECC, secp256k1

import random
from datetime import datetime
from typing import Callable, Optional, List, Dict, Tuple

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender # Sender name
        self.receiver = receiver # Receiver name
        self.amount = amount
        self.signature = None

    def hash_transaction(self) -> str:
        """Return the hash of the transaction."""
        tx_data = f"{self.sender}{self.receiver}{self.amount}"
        return int(SHA256.digest(tx_data), 16)

    def sign(self, private_key: int, curve: ECC = secp256k1):
        """Sign the transaction."""
        h = self.hash_transaction() % curve.n # to ensure h < n
        k = random.randint(1, curve.n - 1) # nonce of the signature
        R = curve.scalar_multiply(k, curve.G)
        r = R[0] % curve.n # x-coordinate of R, mod n

        if r == 0:
            raise ValueError("Invalid r value, retry signing")
        
        k_inv = pow(k, -1, curve.n)
        s = (k_inv * (h + private_key * r)) % curve.n
        if s == 0:
            raise ValueError("Invalid s value, retry signing")
        
        self.signature = (r, s)

    def verify(self, public_key, curve: ECC = secp256k1) -> bool:
        """Verify the signature of the transaction."""
        if self.signature is None:
            return False
        
        r, s = self.signature
        h = self.hash_transaction() % curve.n
        if not (1 <= r < curve.n and 1 <= s < curve.n):
            return False
        
        s_inv = pow(s, -1, curve.n)
        u1 = (h * s_inv) % curve.n
        u2 = (r * s_inv) % curve.n

        # Compute P = u1*G + u2*Q
        P = curve.add_points(
            curve.scalar_multiply(u1, curve.G),
            curve.scalar_multiply(u2, public_key)
        )

        return P[0] % curve.n == r  # Check if x-coord matches r



class Block:
    # NOTE: add the ability to change the hashing logic (e.g. SHA-256, SHA-3, simple XOR based etc.) in the future
    __slots__ = ("_index", "_previous_hash", "_data", "_timestamp", "_nonce", "_hash")
    
    def __init__(
            self, 
            index: int, 
            previous_hash: str, 
            data: List[Transaction], 
            timestamp: datetime.timestamp = None, 
            nonce: int = 0
        ):
        self._index = index
        self._previous_hash = previous_hash
        self._data = data
        self._timestamp = timestamp if timestamp is not None else datetime.now().timestamp()
        self._nonce = nonce
        self._hash = self.compute_hash()

        self.is_signed = False
        self.signed_by = None

    def compute_hash(self) -> str:
        """Compute the block's hash based on its contents."""
        transaction_hashes = "".join(hex(d.hash_transaction())[2:] for d in self._data)
        return SHA256.digest(f"{self._previous_hash}{self._timestamp}{transaction_hashes}{self._nonce}")
           
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
        self._hash = self.compute_hash()
    
    @property
    def hash(self) -> str:
        return self._hash
    
    # Proof of Work:
    def mine(self, criteria: Callable[[str], bool], max_iterations: int = 1000) -> Optional[str]:
        """Perform Proof-of-Work mining until the criteria is met or max iterations is reached."""
        iterations = 0
        while not criteria(self._hash):
            if iterations > max_iterations:
                return None
            self.nonce += 1 # this should update the hash through the setter for nonce
            iterations += 1
        return self._hash

    # Verification:
    def verify_transactions(self, public_keys: Dict[str, Tuple[int, int]]) -> bool:
        """
            Verify all transactions in the block.

            :param public_keys: Public key registry.
            :return: True if all transactions are valid, False otherwise.
        """
        for tx in self._data:
            sender_public_key = public_keys.get(tx.sender)
            if not sender_public_key or not tx.verify(sender_public_key):
                return False
        return True