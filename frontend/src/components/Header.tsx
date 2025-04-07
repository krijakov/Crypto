import React from "react";
import { useUser } from "../context/UserContext";
import styles from "./Header.module.css";

const Header = () => {
    const {user} = useUser();
    return (
        <div className={styles.container}>
            <div><h1>⛏️ Blockchain Miner</h1></div>
            <div><h2>{user?.username}</h2></div>
            
        </div>
    );
};

export default Header;