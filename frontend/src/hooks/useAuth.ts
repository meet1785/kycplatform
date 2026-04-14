"use client";

import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/api";
import { clearAuthTokens, isAuthenticated } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useCallback } from "react";
import Cookies from "js-cookie";

export function useAuth() {
  const router = useRouter();

  const { data: user, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: authApi.getProfile,
    enabled: isAuthenticated(),
    retry: false,
  });

  const logout = useCallback(async () => {
    try {
      const refresh = Cookies.get("refresh_token");
      if (refresh) await authApi.logout(refresh);
    } catch {
      // Ignore errors
    } finally {
      clearAuthTokens();
      router.push("/auth/login");
    }
  }, [router]);

  return { user, isLoading, logout, isAuthenticated: isAuthenticated() };
}
