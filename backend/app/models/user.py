#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Model for user registration and authentication in the blockchain network.

"""

from pydantic import BaseModel, Field
from typing import Tuple

class User(BaseModel):
    """
    User model for registration and authentication.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for the user")

    public_key: Tuple[int, int]# Required for digital signature validation

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility with SQLAlchemy models

    def serialize(self) -> dict:
        """
        Serialize the user object to a dictionary.
        """
        return {
            "username": self.username,
            "public_key": self.public_key,
        }
    
class RegisteredUser(BaseModel):
    """
    Model for already registered users.
    """
    public_key: Tuple[int, int]