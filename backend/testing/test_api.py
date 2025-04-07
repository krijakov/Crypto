#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Tests for the server endpoints.

"""

import sys
from pathlib import Path
parent_dir = Path.cwd().parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir / "app"))

import pytest
import httpx
from uuid import uuid4
from app.blockchain.block import Transaction
from app.blockchain.digital_signature.ecc import secp256k1, ECC
import random

BASE_URL = "http://localhost:8000"

# To ensure unique usernames:
user1 = f"testuser_{uuid4().hex[:6]}"
user2 = f"Ubulka_{uuid4().hex[:6]}"

# Helper: generate keypair
def generate_keys(curve: ECC = secp256k1):
    private_key = random.randint(1, curve.n - 1)
    public_key = curve.scalar_multiply(private_key, curve.G)
    return private_key, public_key

# Set up the client:
@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE_URL)

def test_register_users(client):
    global priv_test, pub_test, priv_ubulka, pub_ubulka

    priv_test, pub_test = generate_keys()
    priv_ubulka, pub_ubulka = generate_keys()

    r1 = client.post("/register", json={
        "username": user1,
        "public_key": pub_test
    })
    assert r1.status_code == 200
    assert r1.json()["success"] == 1

    r2 = client.post("/register", json={
        "username": user2,
        "public_key": pub_ubulka
    })
    assert r2.status_code == 200
    assert r2.json()["success"] == 1

def test_submit_transaction(client):

    tx = Transaction("testuser", "Ubulka", 100.0)
    tx.sign(priv_test)

    action_payload = {
        "action_type": "submit_transaction",
        "action_data": {
            "sender": tx.sender,
            "receiver": tx.receiver,
            "amount": tx.amount,
            "signature": tx.signature
        }
    }

    r = client.post("/submit_action", json=action_payload)
    assert r.status_code == 200
    assert r.json()["action_type"] == "submit_transaction"

def test_info_and_blockchain(client):
    info = client.get("/info")
    assert info.status_code == 200
    assert "users" in info.json()

    chain = client.get("/blockchain")
    assert chain.status_code == 200
    assert "blockchain" in chain.json()