import { api } from "@/lib/api/client";
import type { CurrentUser } from "@/types/auth";

export const authApi = {
  login: (email: string, password: string) =>
    api.post<CurrentUser>("/auth/login", { email, password }),
  logout: () => api.post<void>("/auth/logout", {}),
  me: () => api.get<CurrentUser>("/auth/me"),
};
