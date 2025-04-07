#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Tests for the manual implementation of the ECC digital signature algorithm.

"""
import pytest
import random
from ecdsa import ellipticcurve, curves

import sys
from pathlib import Path
parent_dir = Path.cwd().parent
sys.path.append(str(parent_dir))

from app.blockchain.digital_signature.ecc import ECC, secp256k1

# Official ecdsa implementation
ecdsa_curve = curves.SECP256k1.curve
ecdsa_G = curves.SECP256k1.generator
ecdsa_n = curves.SECP256k1.order

def to_ecdsa_point(point):
    """Convert custom ECC point (x, y) to ecdsa.ellipticcurve.Point"""
    x, y = point
    return ellipticcurve.Point(ecdsa_curve, x, y)

def to_custom_point(point):
    """Convert ecdsa.ellipticcurve.Point to custom ECC point (x, y)"""
    return (point.x(), point.y())

@pytest.mark.parametrize("P, Q", [
    (secp256k1.G, secp256k1.scalar_multiply(2, secp256k1.G)),  # G + 2G = 3G
    (secp256k1.scalar_multiply(3, secp256k1.G), secp256k1.scalar_multiply(5, secp256k1.G)),  # 3G + 5G = 8G
])
def test_point_addition(P, Q):
    """Test ECC point addition"""
    expected = to_ecdsa_point(P) + to_ecdsa_point(Q)
    result = secp256k1.add_points(P, Q)
    assert result == to_custom_point(expected), f"Expected {to_custom_point(expected)}, got {result}"

@pytest.mark.parametrize("P", [
    secp256k1.G,
    secp256k1.scalar_multiply(3, secp256k1.G),
])
def test_point_doubling(P):
    """Test ECC point doubling"""
    expected = to_ecdsa_point(P) + to_ecdsa_point(P)  # P + P
    result = secp256k1.double_point(P)
    assert result == to_custom_point(expected), f"Expected {to_custom_point(expected)}, got {result}"

@pytest.mark.parametrize("d", [
    random.randint(1, secp256k1.n - 1),
    random.randint(1, secp256k1.n - 1),
    random.randint(1, secp256k1.n - 1),
])
def test_scalar_multiplication(d):
    """Test scalar multiplication using Double-and-Add"""
    expected = to_ecdsa_point(secp256k1.G) * d
    result = secp256k1.scalar_multiply(d, secp256k1.G)
    assert result == to_custom_point(expected), f"Expected {to_custom_point(expected)}, got {result}"

@pytest.mark.parametrize("d", [
    random.randint(1, secp256k1.n - 1),
])
def test_key_generation(d):
    """Test that private_key * G matches ecdsa public key"""
    public_key = secp256k1.scalar_multiply(d, secp256k1.G)

