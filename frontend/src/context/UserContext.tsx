import React, { createContext, useCallback, useContext, useEffect, useState, ReactNode } from "react";
import { ECPoint } from "../crypto/ecc";

// User structure:
interface User {
    username: string;
    publicKey: [string, string];
    privateKey: string;
}

// Context type:
interface UserContextType {
    user: User | null;
    setUser: (user: User) => void;
    clearUser: () => void;
}

// Create the context, now typed:
const UserContext = createContext<UserContextType | undefined>(undefined);

// Provider:
export const UserProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUserState] = useState<User | null>(null);

    const setUser = (newUser: User) => {
        setUserState(newUser);
    };

    const clearUser = () => {
        setUserState(null);
    };

    return (
        <UserContext.Provider value={{user, setUser, clearUser}}>
            {children}
        </UserContext.Provider>
    );
};

// Custom hook for convenience, to simplify things:
export const useUser = (): UserContextType => {
    const context = useContext(UserContext);
    if (!context) {
      throw new Error("useUser must be used within a UserProvider");
    }
    return context;
  };

