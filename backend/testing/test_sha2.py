#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Tests for the manual implementation of the SHA-256 hashing algorithm.

"""

import hashlib

import sys
from pathlib import Path
parent_dir = Path.cwd().parent
sys.path.append(str(parent_dir))

from app.blockchain.hashing.sha2 import SHA256

# ✅ Function to compare our SHA-256 against Python's hashlib
def reference_sha256(message: str) -> str:
    return hashlib.sha256(message.encode()).hexdigest()

# ✅ Test Cases
def test_empty_string():
    assert SHA256.digest("") == reference_sha256("")

def test_hello():
    assert SHA256.digest("hello") == reference_sha256("hello")

def test_long_text():
    text = "The quick brown fox jumps over the lazy dog"
    assert SHA256.digest(text) == reference_sha256(text)

def test_longer_text():
    text = "SHA-256 is a cryptographic hash function that produces a fixed-size hash output."
    assert SHA256.digest(text) == reference_sha256(text)

def test_repeated_chars():
    text = "a" * 1000  # A long string of 1000 'a' characters
    assert SHA256.digest(text) == reference_sha256(text)

def test_numbers():
    text = "1234567890"
    assert SHA256.digest(text) == reference_sha256(text)

def test_symbols():
    text = "!@#$%^&*()_+-=[]{}|;:',.<>/?"
    assert SHA256.digest(text) == reference_sha256(text)

def test_unicode():
    text = "こんにちは世界"  # "Hello World" in Japanese
    assert SHA256.digest(text) == reference_sha256(text)