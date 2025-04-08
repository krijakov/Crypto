import React, { useState } from "react";
import axios from "axios";
import { useUser } from "../context/UserContext";
import { generateKeyPair, getPublicFromPrivate } from "../crypto/DigitalSignatureElliptic";
import styles from "./Register.module.css";

const Register = () => {
    const [mode, setMode] = useState<"register" | "login">("register");
    const [username, setUsername] = useState("");
    const [privateKeyInput, setPrivateKeyInput] = useState<string>("");
    const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
    const [returnMessage, setReturnMessage] = useState<string | null>(null);
    const { setUser } = useUser();

    const [showModal, setShowModal] = useState(false);
    const [tempPrivateKey, setTempPrivateKey] = useState<string | null>(null);
    const [showPrivateKey, setShowPrivateKey] = useState(false);

    const handleRegister = async () => {
        try {
            // 1. Generate ECC keys
            const { privateKey, publicKey } = generateKeyPair();

            // 2. Submit to backend
            const register_payload = {
                username,
                public_key: publicKey,
            };

            const res = await axios.post("http://localhost:8000/register", register_payload);

            if (res.data.success === 1) {
                setReturnMessage(res.data.message);
                // 3. Update global state
                setUser({username, privateKey, publicKey});
                // 4. Show modal
                setTempPrivateKey(privateKey);
                setShowModal(true); 
                setStatus("success");
            } else {
                setReturnMessage(res.data.message);
                setStatus("error");
            }
        } catch (error) {
            console.error("Registration error:", error);
            setReturnMessage("Unexpected error during registration.");
            setStatus("error");
        }
    };

    const handleLogin = async () => {
        try {
            const publicKey = getPublicFromPrivate(privateKeyInput);
            const login_payload = {"public_key": publicKey};

            const res = await axios.post("http://localhost:8000/login", login_payload);

            if (res.data.success === 1) {
                setReturnMessage(res.data.message);
                // 3. Update global state
                setUser({username: res.data.username, privateKey: privateKeyInput, publicKey});
                setReturnMessage(`Welcome back, ${res.data.username}!`);
                setStatus("success");
            } else {
                setReturnMessage(res.data.message);
                setStatus("error");
            }

        } catch (error) {
            console.error("Login error:", error);
            setReturnMessage("Unexpected error during login.");
            setStatus("error");
        }
    };

    // Register utilities to show/hide private key
    const copyToClipboard = () => {
        if (tempPrivateKey) {
            navigator.clipboard.writeText(tempPrivateKey);
            alert("Private key copied to clipboard!");
        }
    };

    return (
        <div className={styles.container}>
          <div className={styles.modeSwitcher}>
            <button onClick={() => setMode("register")} disabled={mode === "register"}>
              Register
            </button>
            <button onClick={() => setMode("login")} disabled={mode === "login"}>
              Login
            </button>
          </div>
    
          {mode === "register" ? (
            <div className={styles.form}>
              <h2>Register</h2>
              <input
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <button className={styles.primaryButton} onClick={handleRegister}>Register</button>
            </div>
          ) : (
            <div className={styles.form}>
              <h2>Login</h2>
              <input
                type="text"
                placeholder="Paste your private key"
                value={privateKeyInput}
                onChange={(e) => setPrivateKeyInput(e.target.value)}
              />
              <button className={styles.primaryButton} onClick={handleLogin}>Login</button>
            </div>
          )}
    
          {status === "success" && !showModal && <p className={styles.success}>✅ {returnMessage}</p>}
          {status === "error" && <p className={styles.error}>❌ {returnMessage}</p>}
    
          {showModal && (
            <div className={styles.modalOverlay}>
              <div className={styles.modal}>
                <h2>🎉 Registration Successful</h2>
                <p><strong>Username:</strong> {username}</p>
                <p><strong>Private Key:</strong></p>
                <div className={styles.privateKeyRow}>
                  <input
                    type={showPrivateKey ? "text" : "password"}
                    value={tempPrivateKey ?? ""}
                    readOnly
                  />
                  <button onClick={() => setShowPrivateKey((prev) => !prev)}>
                    {showPrivateKey ? "Hide" : "Show"}
                  </button>
                </div>
                <button className={styles.secondaryButton} onClick={copyToClipboard}>
                  📋 Copy Private Key
                </button>
                <p className={styles.warning}>
                  ⚠️ Save your private key securely. This is the only way to access your account!
                </p>
                <div className={styles.modalFooter}>
                  <button className={styles.primaryButton} onClick={() => setShowModal(false)}>
                    I’ve saved it safely
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      );
};

export default Register;
