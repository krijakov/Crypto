import React from "react";
import { useUser } from "../context/UserContext";
import { Navigate } from "react-router-dom";

const Home = () => {
    const { user } = useUser();
    if (!user) {
        return <Navigate to="/register" />;
    } else {
        return <Navigate to="/transactions" />;
    }
};

export default Home;

