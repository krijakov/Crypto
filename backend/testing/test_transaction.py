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
sys.path.append(str(parent_dir / "app"))

from app.blockchain.digital_signature.ecc import secp256k1
from app.blockchain.block import Transaction

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

def test_invalid_signature():
    """Signature verification should fail with the wrong public key."""
    # Generate first key pair
    priv1 = random.randint(1, secp256k1.n - 1)
    pub1 = secp256k1.scalar_multiply(priv1, secp256k1.G)

    # Generate second key pair
    priv2 = random.randint(1, secp256k1.n - 1)
    pub2 = secp256k1.scalar_multiply(priv2, secp256k1.G)

    tx = Transaction("Alice", "Bob", 42)
    tx.sign(priv1, secp256k1)

    assert not tx.verify(pub2, secp256k1), "Verification should fail with a different public key"