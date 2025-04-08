/*! 
=======================================================================
* Mining React Component
=======================================================================

* Retrieves the pending blocks from the backend, displays them and allows users to mine them.
* The component checks if the user is logged in and redirects to the registration page if not.

*/

import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";
import { useUser } from "../context/UserContext";
import { Block } from "../crypto/Block";
import { manualSign } from "../crypto/DigitalSignatureElliptic";

import styles from "./Mining.module.css";

// 👇 This is how you load a worker in Parcel/Vite/Webpack
const MinerWorker = new URL("../workers/miner.worker.ts", import.meta.url);

const Mining = () => {
    const { user } = useUser();
    const [pendingBlocks, setPendingBlocks] = useState<Block[]>([]);

    // Background mining:
    const [miningStatus, setMiningStatus] = useState<string>("Idle");
    const [worker, setWorker] = useState<Worker | null>(null);

    if (!user) {
        return <Navigate to="/register" />;
    }

    // Retrieve the mining status info from the backend:
    const retrieveBlockInfo = async () => {
        try {
            const response = await axios.get("http://localhost:8000/info");
            const blockInfo = response.data.pending_blocks;
            console.log("Pending blocks:", blockInfo);
            const parsed = blockInfo.map(Block.deserialize);
            setPendingBlocks(parsed);
        } catch (error) {
            console.error("Error retrieving block info:", error);
        }
    }

    useEffect(() => {
        retrieveBlockInfo();
        const interval = setInterval(retrieveBlockInfo, 5_000); // refresh every 5 seconds
        return () => clearInterval(interval);
    }, []);

    // Mining:
    const startMining = (block: Block) => {
        const w = new Worker(new URL("../workers/miner.worker.ts", import.meta.url), { type: "module" });

        w.postMessage({ blockData: JSON.parse(JSON.stringify(block)) });

        w.onmessage = async (e) => {
            const msg = e.data;

            if (msg.type === "progress") {
                setMiningStatus(`⏳ Mining... Attempts: ${msg.nonce}`);
            } else if (msg.type === "solved") {
                setMiningStatus(`✅ Block mined! Nonce: ${msg.nonce}, Hash: ${msg.hash} (in ${msg.time}s)`);
                w.terminate();
                if (block !== null) {
                    // Set the mined block's nonce with the found nonce:
                    block.nonce = msg.nonce.toString();
                    console.log("Nonce:", block.nonce, msg.nonce);
                    // Check if the hashes match:
                    const verifiedBlock = Block.deserialize(JSON.parse(JSON.stringify(block)));
                    verifiedBlock.nonce = msg.nonce.toString();

                    if (verifiedBlock.computeHash() !== msg.hash) {
                        console.error("🚨 Hash mismatch!", verifiedBlock.computeHash(), msg.hash);
                    }
                    // Sign the block with the user's private key:
                    const blockHash = verifiedBlock.computeHash();
                    const signature = manualSign(blockHash, user.privateKey);
                    console.log("Signature:", signature);

                    console.log("Verified block index:", verifiedBlock.index);
                    // Prepare the payload to send to the backend:
                    const MinedBlockValidationPayload = {
                        action_type: "mined_block_validation",
                        action_data: {
                            index: verifiedBlock.index,
                            previous_hash: verifiedBlock.previousHash,
                            timestamp: verifiedBlock.timestamp,
                            nonce: verifiedBlock.nonce,
                            criterion: {
                                type: verifiedBlock.criterion.type,
                                difficulty: verifiedBlock.criterion.difficulty,
                            },
                            miner: user.username,
                            signature: signature
                        }
                    }
                    console.log("Action payload: ", MinedBlockValidationPayload);

                    try {
                        const response = await axios.post("http://localhost:8000/submit_action", MinedBlockValidationPayload);
                        console.log("Mined block submitted:", response.data);
                    }
                    catch (error) {
                        console.error("Error submitting mined block:", error);
                    }
                } else {
                    console.error("Mined block is null!");
                }



            }
        };

        setWorker(w);
    };


    return (
        <div className={styles.container}>
          <h1 className={styles.heading}>⛏️ Mining</h1>
          <p className={styles.status}>{miningStatus}</p>
    
          {pendingBlocks.length === 0 ? (
            <p className={styles.empty}>No pending blocks available.</p>
          ) : (
            <div className={styles.blockList}>
              {pendingBlocks.map((block) => (
                <div key={block.index} className={styles.blockCard}>
                  <div className={styles.blockInfo}>
                    <p><strong>Block:</strong> {block.index}</p>
                    <p><strong>Transactions:</strong> {block.data.length}</p>
                    <p><strong>Difficulty:</strong> {block.criterion.difficulty}</p>
                  </div>
                  <button className={styles.mineButton} onClick={() => startMining(block)}>Mine</button>
                </div>
              ))}
            </div>
          )}
        </div>
      );
};


export default Mining;