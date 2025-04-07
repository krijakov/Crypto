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

    wallet: int = Field(default=0.0, exclude=True)  # backend-only field

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility with SQLAlchemy models