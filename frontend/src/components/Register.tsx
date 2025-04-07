import React, { useState } from "react";
import axios from "axios";
import { useUser } from "../context/UserContext";
import { generateKeyPair } from "../crypto/DigitalSignatureElliptic";

const Register = () => {
    const [username, setUsername] = useState("");
    const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
    const [returnMessage, setReturnMessage] = useState<string | null>(null);
    const { setUser } = useUser();

    const handleRegister = async () => {
        try {
            // 1. Generate ECC keys
            const { privateKey, publicKey } = generateKeyPair();

            // 2. Submit to backend
            const register_payload = {
                username,
                public_key: publicKey, // matches FastAPI pydantic model
            };
            console.log(register_payload);
            const res = await axios.post("http://localhost:8000/register", register_payload);

            if (res.data.success === 1) {
                setReturnMessage(res.data.message);
                // 3. Update global state
                setUser({
                    username,
                    privateKey,
                    publicKey,
                });
                setStatus("success");
            } else {
                setReturnMessage(res.data.message);
                console.log(res.data.message);
                setStatus("error");
            }
        } catch (error) {
            console.error("Registration error:", error);
            setStatus("error");
        }
    };

    return (
        <div style={{ padding: "2rem" }}>
            <h2>Register New User</h2>
            <input
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <button style={{ marginLeft: "1rem" }} onClick={handleRegister}>
                Register
            </button>

            {status === "success" && <p style={{ color: "green" }}>✅ Registered successfully!</p>}
            {status === "error" && <p style={{ color: "red" }}>❌ Registration failed: {returnMessage}</p>}
        </div>
    );
};

export default Register;
