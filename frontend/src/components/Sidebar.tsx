import styles from "./Sidebar.module.css";
import { Link, useLocation } from "react-router-dom";

import { useUser } from "../context/UserContext";

const Sidebar = () => {
  const location = useLocation();
  const { user } = useUser();

  return (
    <div style={{ width: "200px", padding: "1rem", backgroundColor: "#ddd", height: "100vh" }}>
      {user ? (
        <>
          <Link
            to="/transactions"
            className={`${styles.link} ${location.pathname === "/transactions" ? styles.active : ""}`}
          >
            Transactions
          </Link>
          <Link
            to="/mining"
            className={`${styles.link} ${location.pathname === "/mining" ? styles.active : ""}`}
          >
            Mining
          </Link>
        </>
      ) : (
        <Link
          to="/register"
          className={`${styles.link} ${location.pathname === "/register" ? styles.active : ""}`}
        >
          <p style={{ padding: "1rem", fontStyle: "italic" }}>Please register to access features</p>
        </Link>
      )}


    </div>
  );
};

export default Sidebar
