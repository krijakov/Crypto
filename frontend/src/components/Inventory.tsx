/*! 
=======================================================================
* Inventory module
=======================================================================

* Queries the backend for the current state of the blockchain and gathers the owned coins.

*/

import React, { useEffect, useState } from "react";
import axios from "axios";

import { useUser, User } from "../context/UserContext";
import styles from "./Inventory.module.css";

export const Inventory = () => {
    const { user } = useUser();
    const [blockchainState, setBlockchainState] = useState<any>(null);
    const [inventory, setInventory] = useState<number>(0);

    const retrieveBlockchainState = async () => {
        try {
            const response = await axios.get("/api/blockchain");
            const blockchainState = response.data.blockchain;
            setBlockchainState(blockchainState);
            console.log("Blockchain state:", blockchainState);
            return blockchainState;
        } catch (error) {
            console.error("Error retrieving blockchain state:", error);
        }
    }

    const getInventory = (user: User, state: any) => {
        //if (!blockchainState) return null;
        let inventory: number = 0;

        // Iterate over the blocks and transactions to calculate the inventory:
        for (const block of state.blocks) {
            for (const transaction of block.transactions) {
                if (transaction.sender === user.username) {
                    inventory -= transaction.amount;
                    //console.log("Subtracting from:", user.username, "amount:", transaction.amount);
                }
                if (transaction.receiver === user.username) {
                    //console.log("Adding to:", user.username, "amount:", transaction.amount);
                    inventory += transaction.amount;
                }
            }
        }
        console.log("Inventory:", inventory);
        setInventory(inventory);
        return inventory;
    }

    const refreshInventory = async () => {
        const state = await retrieveBlockchainState();
        console.log("User:", user?.username);
        if (!user || !state) return;
        getInventory(user, state);
    }

    useEffect(() => {
        refreshInventory();
        const interval = setInterval(refreshInventory, 5_000); // refresh every 5 seconds
        return () => clearInterval(interval);
    }, [user]);

    // Return the inventory information:
    return (
        <div className={styles.inventoryContainer}>
            {blockchainState ? (
                <p className={styles.inventoryText}>🪙 {inventory} coins</p>
            ) : (
                <p className={styles.inventoryText}>Loading...</p>
            )}
        </div>
    );

}