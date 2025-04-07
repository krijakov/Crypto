#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Model for a serializable mining criterion.
This model is used to define the mining criterion for the blockchain.

"""

from pydantic import BaseModel

class MiningCriterion(BaseModel):
    type: str # e.g. "leading_zeros"
    difficulty: int

    def check(self, hash_str: str) -> bool:
        """
        Check if the hash string meets the mining criterion.
        """
        if self.type == "leading_zeros":
            return hash_str.startswith("0" * self.difficulty)
        else:
            raise ValueError(f"Unknown mining criterion type: {self.type}")
        
    def serialize(self) -> dict:
        """
        Serialize the mining criterion to a dictionary.
        """
        return {
            "type": self.type,
            "difficulty": self.difficulty
        }
    
    @staticmethod
    def from_dict(data: dict) -> "MiningCriterion":
        return MiningCriterion(
            type=data.get("type"),
            difficulty=data.get("difficulty")
        )