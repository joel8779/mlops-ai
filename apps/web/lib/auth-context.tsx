"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { authApi, setTokens, clearTokens, getAccessToken } from "./api";

interface AuthContextType {
  user: any | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const initAuth = async () => {
      const token = getAccessToken();
      if (token && mounted) {
        try {
          // Validate token with backend before setting user state
          const userData = await authApi.me();
          if (mounted) {
            setUser(userData);
          }
        } catch (error) {
          console.error("Failed to validate token:", error);
          // Token is invalid or expired - clear session
          clearTokens();
          if (mounted) {
            setUser(null);
          }
        }
      }
      if (mounted) {
        setLoading(false);
      }
    };

    initAuth();

    return () => {
      mounted = false;
    };
  }, []);

  const refreshUser = async () => {
    try {
      const userData = await authApi.me();
      setUser(userData);
    } catch (error) {
      console.error("Failed to fetch user:", error);
      clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    setTokens(response.access_token, response.refresh_token);
    await refreshUser();
  };

  const register = async (data: RegisterData) => {
    const response = await authApi.register(data);
    setTokens(response.access_token, response.refresh_token);
    await refreshUser();
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
