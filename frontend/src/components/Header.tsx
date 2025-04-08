import React from "react";
import { useUser } from "../context/UserContext";
import styles from "./Header.module.css";
import logoUrl from "url:../assets/logo.png";

const Header = () => {
    const {user} = useUser();
    return (
        <header className={styles.container}>
            <div className={styles.brand}>
                <img src={logoUrl} alt="Blockchain Miner Logo" className={styles.logo} />
                <span className={styles.title}>Blockchain Miner</span>
            </div>
            <div className={styles.userInfo}>
                {user && <span className={styles.username}>👤 {user.username}</span>}
            </div>
        </header>
    );
};

export default Header;