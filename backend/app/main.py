#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Main FastAPI application for the blockchain network.

"""

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from logging import Logger
import json
from pathlib import Path

from models.user import User
from models.actions import Action
from models.mining_criterion import MiningCriterion
from engine.engine import Engine
from blockchain.blockchain import Blockchain
from configs import configs, logger, get_logger

# Initialize the action queue, the blockchain and the engine:
action_queue = asyncio.Queue()
engine_criterion = MiningCriterion(type=configs.MINING_TYPE, difficulty=configs.MINING_DIFFICULTY)
blockchain = Blockchain(criterion=engine_criterion)
if Path(configs.BLOCKCHAIN_LOCATION).is_file():
    blockchain.load_from_json(configs.BLOCKCHAIN_LOCATION) 
engine = Engine(blockchain, logger)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bind the global instances (to be able to yield them):
    app.state.engine = engine
    app.state.action_queue = action_queue
    loop = asyncio.get_event_loop()
    loop.create_task(engine.process_action(action_queue)) # start the engine in the background

    logger.info("🚀 Engine initialized, action processor running.")
    yield

    logger.info("🧹 Server shutting down...")
    # Optionally persist blockchain, save state here:
    with open(configs.BLOCKCHAIN_LOCATION, "w", encoding='utf-8') as bf:
        json.dump(app.state.engine.blockchain.json_serialize(), bf, indent=4)

# Create the app:
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set the title and description of the app:
app.title = "Blockchain Network API"
app.description = "API for interacting with the blockchain network."
app.version = "1.0.0"

def get_engine(request: Request) -> Engine:
    return request.app.state.engine

# User registration and login:
@app.post("/register")
async def register_user(
        user: User,
        engine: Engine = Depends(get_engine),
        logger: Logger = Depends(get_logger)
    ):
    """
    Register a new user with the given username and public key.
    """
    try:
        engine.add_user(user=user)
        return {"message": "User registered successfully", "username": user.username, "success": 1}
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return {"message": f"Error registering user: {e}", "username": user.username, "success": 0}

@app.post("/login")
async def login_user(
        user: User,
        engine: Engine = Depends(get_engine),
        logger: Logger = Depends(get_logger)  
    ):
    """
    Log in a user with the given username and public key.
    """
    try:
        engine.verify_user(user)
        return {"message": "User logged in successfully", "username": user.username, "success": 1}
    except Exception as e:
        logger.error(e)
        return {"message": f"User login failed: {e}", "username": user.username, "success": 0}

# Submit an action:
@app.post("/submit_action")
async def submit_action(request: Request):
    """
    Submit an action to the blockchain network.
    """
    raw = await request.json()
    action_type = raw.get("action_type") # check if the request has an action type field

    if not action_type or action_type not in Action.registry:
        raise HTTPException(status_code=400, detail="Invalid or missing action_type")
    
    ActionClass = Action.registry[action_type] # select the action class

    try:
        action = ActionClass(**raw)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid action payload: {e}")

    await action_queue.put(action)
    return {"message": "Action submitted successfully", "action_type": action_type}

# Get info on the current transactions and blocks:
@app.get("/info")
async def get_blockchain_info(engine: Engine = Depends(get_engine)):
    """
    Get the current status of the system.
    """
    return {
        "users": [
            {   
                "username": user.username,
                "public_key": user.public_key,
                "wallet": user.wallet
            } for user in engine.current_users.values()
        ],
        "pending_blocks": [
            {
                "index": block.index,
                "data": [tr.json_serialize() for tr in block.data],
                "previousHash": block.previous_hash, # NOTE: the keys should match the frontend keys for unified (de)serialization there
                "timestamp": block.timestamp,
                "finalized": block.finalized,
                "criterion": block.criterion.serialize(),
            } for block in engine.pending_blocks.values()
        ],
        "pending_transactions": [
            {
                "sender": tx.sender,
                "receiver": tx.receiver,
                "amount": tx.amount
            } for tx in engine.pending_transactions
        ]
    }

@app.get("/blockchain")
async def get_blockchain(engine: Engine = Depends(get_engine)):
    """Endpoint to get the complete blockchain."""
    return {
        "blockchain": engine.blockchain.json_serialize()
    }
    

if __name__ == "__main__":
    server_config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
    server = uvicorn.Server(config=server_config)
    server.run() # uvicorn main:app --host 0.0.0.0 --port 8000