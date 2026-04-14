import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = Cookies.get("refresh_token");
        const response = await axios.post(`${API_URL}/api/v1/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        Cookies.set("access_token", access, { expires: 1 });
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch {
        // Redirect to login
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
        if (typeof window !== "undefined") {
          window.location.href = "/auth/login";
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
