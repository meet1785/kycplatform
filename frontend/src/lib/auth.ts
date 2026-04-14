import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";

interface TokenPayload {
  user_id: string;
  email: string;
  full_name: string;
  is_phone_verified: boolean;
  exp: number;
}

const isProduction = process.env.NODE_ENV === "production";

export const setAuthTokens = (access: string, refresh: string) => {
  Cookies.set("access_token", access, { expires: 1, secure: isProduction, sameSite: "strict" });
  Cookies.set("refresh_token", refresh, { expires: 7, secure: isProduction, sameSite: "strict" });
};

export const clearAuthTokens = () => {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
};

export const getAccessToken = () => Cookies.get("access_token");

export const isAuthenticated = (): boolean => {
  const token = getAccessToken();
  if (!token) return false;
  try {
    const decoded = jwtDecode<TokenPayload>(token);
    return decoded.exp * 1000 > Date.now();
  } catch {
    return false;
  }
};

export const getUserFromToken = (): TokenPayload | null => {
  const token = getAccessToken();
  if (!token) return null;
  try {
    return jwtDecode<TokenPayload>(token);
  } catch {
    return null;
  }
};
