#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Async execution engine for the queued actions.

"""

import asyncio
from typing import Dict, List, Tuple
from logging import Logger
import json

from models.user import User
from models.mining_criterion import MiningCriterion
from blockchain.blockchain import Blockchain
from blockchain.block import Transaction, Block
from blockchain.digital_signature.ecc import ECC, secp256k1
from blockchain.hashing.sha2 import SHA256
from configs import configs


class Engine:
    def __init__(self, blockchain: Blockchain, logger: Logger):
        """

        The main engine of the blockchain system.
        
        """
        self.logger = logger
        # Keep track of users:
        self.current_users: Dict[str, User] = {} # users by name, usernames should be unique!

        # Connect to the blockchain:
        self.blockchain: Blockchain = blockchain
        self.criterion: MiningCriterion = blockchain.criterion

        # Temporary storage for pending transactions:
        self.pending_transactions: List[Transaction] = []
        self.pending_blocks: Dict[int, Block] = {} # blocks by their uuid

        # Optional control variables...
        self.max_pending_transactions = configs.PENDING_TRANSACTIONS # max number of pending transactions

    def add_user(self, user: User):
        """
        Add a user to the system.
        """
        if user.username in self.current_users:
            raise ValueError(f"Name {user.username} already taken. Choose another unique name.")
        else:
            self.logger.info("Adding user, from the engine btw.")
            self.current_users[user.username] = user # only add if it does not exist

    def remove_user(self, user: User):
        """
        Remove a user from the system.
        """
        if user.username in self.current_users:
            del self.current_users[user.username]
        else:   
            self.logger.error(f"User {user.username} not found.")

    def get_user(self, public_key: Tuple[int, int]) -> User:
        """
        Get a user by their public key.
        """
        for user in self.current_users.values():
            if user.public_key == public_key:
                return user
        raise ValueError(f"User with public key {public_key} not found.")

    def verify_user(self, user: User):
        if user.username in self.current_users:
            if user.public_key == self.current_users[user.username].public_key:
                return True
            else:
                raise ValueError(f"User public key missmatch!")
        else:
            raise ValueError(f"User not found, try registering.")
        
    def load_users(self, user_json_path: str):
        """
        Load users from a JSON file.
        """
        try:
            with open(user_json_path, "r", encoding='utf-8') as uf:
                users = json.load(uf)
                for user_data in users:
                    user = User(**user_data)
                    self.add_user(user)
                self.logger.info("Users loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")

    def serialize_users(self) -> str:
        """Serialize the current users to a JSON string."""
        try:
            return [user.serialize() for user in self.current_users.values()]
        except Exception as e:
            self.logger.error(f"Error serializing users: {e}")
            return ""

    def verify_signature(self, data: str, signature: Tuple[int, int], public_key: int, curve: ECC = secp256k1):
        """Verify a digital signature with the public key."""
        if signature is None or public_key is None:
            return False
        
        r,s = signature
        h = int(SHA256.digest(data), 16) % curve.n
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

    def verify_block(self, block: Block):
        """Verify the transactions inside a block."""
        try:
            for tx in block.data:
                assert tx.verify(self.current_users.get(tx.sender).public_key), f"Invalid signature in transaction: {tx}"
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    async def process_action(self, queue: asyncio.Queue):
        """
        Process actions from the queue.
        """
        self.logger.info("🚀 Action processor started!")
        self.logger.info(f"Queue size: {queue.qsize()}")
        while True:
            action = await queue.get()
            if action is not None:
                self.logger.info(f"Executing action: {action.action_type}")
                action(self)
                self.logger.info(self.pending_transactions)
                self.logger.info(f"Blocks to verify: {self.pending_blocks}")