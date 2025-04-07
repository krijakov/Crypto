#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Single block from the blockchain.

"""
from blockchain.hashing.sha2 import SHA256
from blockchain.digital_signature.ecc import ECC, secp256k1
from models.mining_criterion import MiningCriterion

import random
import json
from datetime import datetime
from typing import Callable, Optional, List, Dict, Tuple
from configs import logger

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int, signature = None):#, logger=logger):
        self.sender = sender # Sender name
        self.receiver = receiver # Receiver name
        self.amount = amount
        self.signature = signature # Signed by the sender

        #self.logger = logger

    @classmethod
    def load_from_dict(cls, data: dict):
        return cls(
            sender=data.get("sender"),
            receiver=data.get("receiver"),
            amount=data.get("amount"),
            signature=data.get("signature")
        )
        

    def hash_transaction(self) -> str:
        """Return the hash of the transaction."""
        tx_data = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": int(self.amount)
        }
        # Canonical json serialization for consistant hashes:
        json_data = json.dumps(tx_data, separators=(",", ":"), sort_keys=True)
        #self.logger.info(f"Canonical JSON (backend): {json_data}")
        #self.logger.info(f"Hash (backend): {SHA256.digest(json_data)}")
        return int(SHA256.digest(json_data), 16)

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
            self.logger.error("Signature is None")
            return False
        
        r, s = self.signature
        r = int(r)
        s = int(s)
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
        #self.logger.info(f"r = {r}, s = {s}, h = {h}")
        #self.logger.info(f"P = {P[0] % curve.n}")
        return P[0] % curve.n == r  # Check if x-coord matches r
    
    def json_serialize(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "signature": self.signature
        }

class Block:
    # NOTE: add the ability to change the hashing logic (e.g. SHA-256, SHA-3, simple XOR based etc.) in the future
    __slots__ = ("_index", "_previous_hash", "_data", "_timestamp", "_nonce", "_hash", "_canonical_hash","_criterion", "is_signed", "signed_by", "finalized")
    
    def __init__(
            self, 
            index: int, 
            previous_hash: str, 
            data: List[Transaction], 
            criterion: MiningCriterion,
            timestamp: str = None, 
            nonce: int = 0
        ):
        self._index = index
        self._previous_hash = previous_hash
        self._data = data
        self._timestamp = timestamp if timestamp is not None else str(datetime.now().timestamp())
        self._nonce = nonce
        self._hash = self.compute_hash()
        self._canonical_hash = self.compute_canonical_hash()
        self._criterion = criterion

        self.is_signed = False
        self.signed_by = None

        self.finalized = False

    @classmethod
    def load_from_dict(cls, data: dict):
        transactions = [Transaction.load_from_dict(tx) for tx in data["transactions"]]
        # NOTE: having a proper hash will be checked upon validating the chain
        block = cls(
            index=data["id"],
            previous_hash=data["previous_hash"],
            data=transactions,
            criterion=MiningCriterion.from_dict(data["criterion"]),
            timestamp=data["timestamp"],
            nonce=data["nonce"]
        )
        block.finalized = data["finalized"]
        return block

    def compute_hash(self) -> str:
        """Compute the block's hash based on its contents."""
        transaction_hashes = "".join(hex(d.hash_transaction())[2:] for d in self._data)
        return SHA256.digest(f"{self._previous_hash}{self._timestamp}{transaction_hashes}{self._nonce}")
    
    def compute_canonical_hash(self) -> str:
        """Compute the canonical hash of the block."""
        transaction_hashes = "".join(hex(d.hash_transaction())[2:] for d in self._data)
        return SHA256.digest(f"{self._previous_hash}{self._timestamp}{transaction_hashes}")
           
    @property
    def index(self) -> int:
        return self._index
    
    @index.setter
    def index(self, value: int):
        self._index = value
        self._hash = self.compute_hash()
        self._canonical_hash = self.compute_canonical_hash()
    
    @property
    def previous_hash(self) -> str:
        return self._previous_hash
    
    @previous_hash.setter
    def previous_hash(self, value: str):
        self._previous_hash = value
        self._hash = self.compute_hash()
        self._canonical_hash = self.compute_canonical_hash()

    @property
    def data(self) -> str:
        return self._data
    
    @property
    def criterion(self) -> MiningCriterion:
        return self._criterion
    
    @property
    def timestamp(self) -> str:
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, value: str):
        self._timestamp = value

    @property
    def nonce(self) -> int:
        return self._nonce
    
    @nonce.setter
    def nonce(self, value: int):
        self._nonce = value
        self._hash = self.compute_hash()
        # no canocnical hash update, as it is not needed
    
    @property
    def hash(self) -> str:
        return self._hash
    
    @property
    def canonical_hash(self) -> str:
        return self._canonical_hash
    
    def json_serialize(self):
        return {
            "id": self.index,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "timestamp": self.timestamp,
            "finalized": self.finalized,
            "nonce": self.nonce,
            "transactions": [tx.json_serialize() for tx in self.data],
            "criterion": self.criterion.serialize()
        }

    # deprecated:

    # Proof of Work:
    def mine(self, criteria: Callable[[str], bool], max_iterations: int = 1000) -> Optional[str]:
        """Perform Proof-of-Work mining until the criteria is met or max iterations is reached."""
        iterations = 0
        while not criteria(self._hash):
            if iterations > max_iterations:
                return None
            self.nonce += 1 # this should update the hash through the setter for nonce
            iterations += 1
        self.finalized = True
        return self._hash

    # Verification:
    def verify_transactions(self, public_keys: Dict[str, Tuple[int, int]]) -> bool:
        """
            Verify all transactions in the block.

            :param public_keys: Public key registry.
            :return: True if all transactions are valid, False otherwise.
        """
        for tx in self._data:
            signed_public_key = public_keys.get(self.signed_by)
            if not signed_public_key or not tx.verify(signed_public_key):
                return False
        return True