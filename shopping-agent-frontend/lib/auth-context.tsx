"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

type AuthContextValue = {
  token: string | null;
  username: string | null;
  isLoading: boolean;
  login: (token: string, username: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// NOTE: token stored in localStorage for simplicity in this MVP.
// If this ever needs to be hardened against XSS, migrate to an httpOnly
// cookie issued by the backend instead -- see security notes in project chat.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    const storedUsername = localStorage.getItem("username");
    if (storedToken) setToken(storedToken);
    if (storedUsername) setUsername(storedUsername);
    setIsLoading(false);
  }, []);

  function login(newToken: string, newUsername: string) {
    localStorage.setItem("access_token", newToken);
    localStorage.setItem("username", newUsername);
    setToken(newToken);
    setUsername(newUsername);
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    setToken(null);
    setUsername(null);
  }

  return (
    <AuthContext.Provider value={{ token, username, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
