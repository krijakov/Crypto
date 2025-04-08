import styles from "./Sidebar.module.css";
import { Link, useLocation } from "react-router-dom";

import { useUser } from "../context/UserContext";
import { Inventory } from "./Inventory";

const Sidebar = () => {
  const location = useLocation();
  const { user } = useUser();


  return (
    <aside className={styles.sidebar}>
      <div className={styles.navSection}>
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
            <p className={styles.registerText}>Please register to access features</p>
          </Link>
        )}
      </div>

      {/* Inventory fixed at the bottom */}
      <div className={styles.inventorySection}>
        <Inventory />
      </div>
    </aside>
  );
};

export default Sidebar
