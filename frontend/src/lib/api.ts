import apiClient from "@/lib/axios";
import type {
  LoginCredentials,
  RegisterData,
  User,
  KYCApplication,
  KYCDocument,
  Notification,
  PaginatedResponse,
} from "@/types";

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await apiClient.post("/auth/login/", credentials);
    return response.data;
  },
  register: async (data: RegisterData) => {
    const response = await apiClient.post("/auth/register/", data);
    return response.data;
  },
  logout: async (refresh: string) => {
    const response = await apiClient.post("/auth/logout/", { refresh });
    return response.data;
  },
  getProfile: async (): Promise<User> => {
    const response = await apiClient.get("/auth/profile/");
    return response.data;
  },
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch("/auth/profile/", data);
    return response.data;
  },
  requestOTP: async (data: { phone_number?: string; otp_type: string }) => {
    const response = await apiClient.post("/auth/otp/request/", data);
    return response.data;
  },
  verifyOTP: async (data: { code: string; otp_type: string }) => {
    const response = await apiClient.post("/auth/otp/verify/", data);
    return response.data;
  },
  changePassword: async (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    const response = await apiClient.post("/auth/password/change/", data);
    return response.data;
  },
};

// KYC API
export const kycApi = {
  getApplication: async (): Promise<KYCApplication> => {
    const response = await apiClient.get("/kyc/application/");
    return response.data;
  },
  updateApplication: async (data: Partial<KYCApplication>): Promise<KYCApplication> => {
    const response = await apiClient.put("/kyc/application/", data);
    return response.data;
  },
  submitApplication: async () => {
    const response = await apiClient.post("/kyc/application/submit/");
    return response.data;
  },
  getDocuments: async (): Promise<KYCDocument[]> => {
    const response = await apiClient.get("/kyc/documents/");
    return response.data;
  },
  uploadDocument: async (formData: FormData): Promise<KYCDocument> => {
    const response = await apiClient.post("/kyc/documents/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },
  getDocumentSignedUrl: async (documentId: string) => {
    const response = await apiClient.get(`/kyc/documents/${documentId}/`);
    return response.data;
  },
  deleteDocument: async (documentId: string) => {
    await apiClient.delete(`/kyc/documents/${documentId}/`);
  },
};

// Notifications API
export const notificationsApi = {
  getNotifications: async (): Promise<PaginatedResponse<Notification>> => {
    const response = await apiClient.get("/notifications/");
    return response.data;
  },
  markAsRead: async (notificationId: string): Promise<Notification> => {
    const response = await apiClient.patch(`/notifications/${notificationId}/read/`);
    return response.data;
  },
  markAllAsRead: async () => {
    const response = await apiClient.post("/notifications/mark-all-read/");
    return response.data;
  },
};
