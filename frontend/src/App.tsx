import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import Header from "./components/Header";
import Home from "./components/Home";
import Mining from "./components/Mining";
import Transactions from "./components/Transactions";
import NotFound from "./components/NotFound";
import Sidebar from "./components/Sidebar";
import Register from "./components/Register";
import { UserProvider } from "./context/UserContext";

import styles from "./App.module.css";

const App = () => {
  return (
    <UserProvider>
      <Router future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <div className={styles.mainContent}>
          <Header />
          <div className={styles["app-layout"]}>
            <Sidebar />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/mining" element={<Mining />} />
              <Route path="/register" element={<Register />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </div>
      </Router>
    </UserProvider>
  );
};

export default App;