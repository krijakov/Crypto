#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Tests for the Transaction class (digital signature system).

"""

import pytest
import random

import sys
from pathlib import Path
parent_dir = Path.cwd().parent
sys.path.append(str(parent_dir))

from src.digital_signature.ecc import ECC, secp256k1
from src.blockchain.block import Transaction

@pytest.mark.parametrize("sender, receiver, amount", [
    ("Alice", "Bob", 10),
    ("Charlie", "David", 50),
    ("Eve", "Frank", 100),
])
def test_ecdsa_signature(sender, receiver, amount):
    """Test ECDSA signing & verification."""
    private_key = random.randint(1, secp256k1.n - 1)
    public_key = secp256k1.scalar_multiply(private_key, secp256k1.G)

    tx = Transaction(sender, receiver, amount)
    tx.sign(private_key, secp256k1)

    assert tx.verify(public_key, secp256k1), "Signature verification failed!"