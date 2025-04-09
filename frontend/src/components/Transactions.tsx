import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";
import styles from "./Transactions.module.css";
import { useUser } from "../context/UserContext";
import { manualSign } from "../crypto/DigitalSignatureElliptic";
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
  const [showConfirmation, setShowConfirmation] = useState(false);

  if (!user) {
    return <Navigate to="/register" />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const tx = new Transaction(
      user.username,
      receiver,
      Number(amount),
      ["", ""]
    );
    const canonicalString = tx.serialize();
    const signature = manualSign(canonicalString, user.privateKey);
    tx.signature = signature;

    const payload = {
      action_type: "submit_transaction",
      action_data: {
        ...tx
      },
    };
    console.log(payload);
    try {
      const res = await axios.post("/api/submit_action", payload);
      console.log("Transaction submitted:", res.data);
      setShowConfirmation(true);
    } catch (error) {
      console.error("Transaction failed:", error);
    }
  };

  return (
    <div className={styles.container}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <h2 className={styles.heading}>Send Coins</h2>

        <label className={styles.label}>
          Receiver
          <input
            type="text"
            className={styles.input}
            value={receiver}
            onChange={(e) => setReceiver(e.target.value)}
            required
          />
        </label>

        <label className={styles.label}>
          Amount
          <input
            type="number"
            className={styles.input}
            min="0"
            step="any"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            required
          />
        </label>

        <button className={styles.button} type="submit">
          Submit Transaction
        </button>
      </form>
      {showConfirmation && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>📤 Transaction Submitted</h3>
            <p>Your transaction has been added to the pool and will be included in a block soon.</p>
            <div className={styles.modalFooter}>
              <button className={styles.primaryButton} onClick={() => setShowConfirmation(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>

  );
};

export default Transactions;
