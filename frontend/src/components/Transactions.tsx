import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";
import SHA256 from "crypto-js/sha256";
import styles from "./Transactions.module.css";
import { useUser } from "../context/UserContext";
//import { digitalSign, sha256, verifySignature } from "../crypto/deprecated/DigitalSignature";
import { manualSign} from "../crypto/DigitalSignatureElliptic";
import { Transaction } from "../crypto/Block";

// To match the python backend, we need to sort the keys in the JSON object
// and remove any whitespace. This is important for the signature to be valid.
export function canonicalizeTransaction(tx: {
    sender: string;
    receiver: string;
    amount: number;
}): string {
    const ordered = {
        amount: tx.amount,
        receiver: tx.receiver,
        sender: tx.sender,
    };

    // Serialize canonically: sorted keys, no whitespace
    return JSON.stringify(ordered, Object.keys(ordered).sort(), 0);
}

const Transactions = () => {
    const { user } = useUser();
    const [receiver, setReceiver] = useState("");
    const [amount, setAmount] = useState<number>(0);

    if (!user) {
        return <Navigate to="/register" />;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const txData = {
            sender: user.username,
            receiver,
            amount: Number(amount),
        };

        const tx = new Transaction(
            user.username,
            receiver,
            Number(amount), 
            ["", ""]
        );
        const canonicalString = tx.serialize();
        //console.log("Canonical JSON (frontend):", canonicalString);
        //console.log("🧪 Frontend hash (hex):", SHA256(canonicalString).toString());
        const signature = manualSign(canonicalString, user.privateKey);
        tx.signature = signature;
        //console.log("Signature (frontend)", signature);
        //const valid = manualVerify(canonicalString, signature, user.publicKey);
        //console.log("🧪 Signature valid (frontend)?", valid);

        const payload = {
            action_type: "submit_transaction",
            action_data: {
                ...tx
            },
        };
        console.log(payload);
        try {
            const res = await axios.post("http://localhost:8000/submit_action", payload);
            console.log("Transaction submitted:", res.data);
        } catch (error) {
            console.error("Transaction failed:", error);
        }
    };

    return (
        <div className={styles.container}>
            <form className={styles.form} onSubmit={handleSubmit}>
                <h2>Send Coins</h2>
                <label>
                    Receiver:
                    <input
                        type="text"
                        value={receiver}
                        onChange={(e) => setReceiver(e.target.value)}
                        required
                    />
                </label>

                <label>
                    Amount:
                    <input
                        type="number"
                        min="0"
                        step="any"
                        value={amount}
                        onChange={(e) => setAmount(Number(e.target.value))}
                        required
                    />
                </label>

                <button type="submit">Send Transaction</button>
            </form>

            <div className={styles.profile}>
                <h3>Profile</h3>
                <p><strong>Username:</strong> {user?.username}</p>
            </div>
        </div>
    );
};

export default Transactions;
