#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Models for available actions.

"""

from pydantic import BaseModel, Field, field_validator
from typing import Tuple, Dict, Type, Literal, ClassVar
from uuid import uuid4

from engine.engine import Engine
from blockchain.block import Block, Transaction
from models.mining_criterion import MiningCriterion
from configs import configs, logger

class Action(BaseModel):
    """
    Base class for all actions in the blockchain network.
    """
    action_type: str = Field(..., description="Type of the action")
    action_data: dict = Field(..., description="Data associated with the action")

    # Registry of subclasses
    registry: ClassVar[Dict[str, Type["Action"]]] = {}

    def __init_subclass__(cls): # hook to automatically register the subclasses upon declaring them.
        if hasattr(cls, "action_type"):
            Action.registry[cls.action_type.__args__[0]] = cls

#------------------------------------------TRANSACTION-----------------------------------------

class TransactionData(BaseModel):
    sender: str
    receiver: str
    amount: int
    signature: Tuple[str, str]

    @field_validator("signature")
    def validate_and_cast_signature(cls, v):
        try:
            return (int(v[0]), int(v[1]))
        except Exception:
            raise ValueError("Invalid signature values, must be convertible to int")

class SubmitTransaction(Action):
    """
    Action for submitting a transaction to the blockchain network.
    """
    action_type: str = Literal["submit_transaction"]
    # Action data has the fields: sender, receiver, amount, signature:
    action_data: TransactionData

    def __call__(self, engine: Engine):
        try:
            transaction = Transaction(
                sender=self.action_data.sender, 
                receiver=self.action_data.receiver,
                amount=self.action_data.amount,
                signature=(int(self.action_data.signature[0]), int(self.action_data.signature[1]))
            ) 

            # Verify transaction:
            assert transaction.verify(engine.current_users.get(self.action_data.sender).public_key), "Transaction signature invalid."
            # Verify if sender and receiver exist:
            assert transaction.sender in engine.current_users and transaction.receiver in engine.current_users, "Sender or receiver doesn't exist"

            # Optionally add the check to check the balances (for now we allow negative wallets).

            if len(engine.pending_transactions) < engine.max_pending_transactions:
                engine.pending_transactions.append(transaction)
                engine.pending_transactions.sort(key=lambda tx: tx.hash_transaction()) # sort the transactions deterministically
            if len(engine.pending_transactions) >= engine.max_pending_transactions:
                # create a block from the pending transactions:
                index = str(uuid4()) # create a unique ID for the block
                new_block = Block(index=index, previous_hash=engine.blockchain.chain[-1].hash, data=engine.pending_transactions, criterion=engine.criterion)
                engine.pending_blocks[index] = new_block

                # reset the pending transactions and add the new one:
                engine.pending_transactions = []
            return True
        except Exception as e:
            logger.error(f"Error during transaction submission: {e}")
            return False

# -----------------------------------------MINING-----------------------------------------

class CriterionData(BaseModel):
    type: str
    difficulty: int

    def serialize(self) -> dict:
        return {
            "type": self.type,
            "difficulty": self.difficulty
        }

class BlockValidationData(BaseModel):
    index: str
    previous_hash: str
    timestamp: str
    nonce: int
    criterion: CriterionData

    miner: str # username of the miner
    signature: Tuple[str, str] # signature of the miner, signing the block hash

class MinedBlockValidation(Action):
    action_type: str = Literal["mined_block_validation"]
    action_data: BlockValidationData
        
    def __call__(self, engine: Engine):
        try:
            # get the relevant block from the engine:
            backend_version = engine.pending_blocks.get(self.action_data.index)
            if backend_version is None:
                logger.error(f"Block not found with ID: {self.action_data.index}")
                return False
            
            # The proposed block to add to the blockchain:
            to_be_verified = Block(
                index=self.action_data.index, 
                previous_hash=self.action_data.previous_hash, 
                data=backend_version.data, 
                criterion=MiningCriterion.from_dict(self.action_data.criterion.serialize()), 
                timestamp=self.action_data.timestamp, 
                nonce=self.action_data.nonce
            )

            # Verify the block:
            # Verify the canonical hash: 
            # NOTE: this prevents maliciously redirecting the block into one containing different transactions.
            assert to_be_verified.canonical_hash == backend_version.canonical_hash, "Invalid previous hash."

            #Verify transactions:
            assert engine.verify_block(to_be_verified), "Invalid transactions in block."
            # Verify PoW:
            assert engine.criterion.check(to_be_verified.compute_hash()), f"Block hash doesn't satisfy PoW: {to_be_verified.nonce}"
            # Verify miner identity and signature:
            signature_data = to_be_verified.compute_hash()
            int_signature = (int(self.action_data.signature[0]), int(self.action_data.signature[1]))
            assert engine.verify_signature(signature_data, int_signature, engine.current_users.get(self.action_data.miner).public_key), "Miner signature invalid"

            # Finalize the block:
            to_be_verified.finalized = True

            # Add the block to the blockchain:
            assert engine.blockchain.add_block(to_be_verified), "Block doesn't match the blockchain."

            # Remove the block from the pending blocks:
            engine.logger.info(f"Block {self.action_data.index} mined by {self.action_data.miner}, added to the blockchain.")
            del engine.pending_blocks[self.action_data.index]
            return True
        except Exception as e:
            logger.error(f"Error during Mined Block Validation: {e}")
            return False
        
#action_lookup = {
#    "submit_transaction": SubmitTransaction,
#    "mined_block_validation": BlockValidationData
#}