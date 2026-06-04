import { create } from "zustand";

import type { User } from "../types/dashboard";

interface AuthState {
  token: string | null;
  user: User | null;
  setSession: (token: string, user: User) => void;
  clearSession: () => void;
}

const persistedToken = localStorage.getItem("thriftcloud.token");
const persistedUser = localStorage.getItem("thriftcloud.user");

export const useAuthStore = create<AuthState>((set) => ({
  token: persistedToken,
  user: persistedUser ? JSON.parse(persistedUser) : null,
  setSession: (token, user) => {
    localStorage.setItem("thriftcloud.token", token);
    localStorage.setItem("thriftcloud.user", JSON.stringify(user));
    set({ token, user });
  },
  clearSession: () => {
    localStorage.removeItem("thriftcloud.token");
    localStorage.removeItem("thriftcloud.user");
    set({ token: null, user: null });
  }
}));

