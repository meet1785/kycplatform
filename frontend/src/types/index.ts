// Auth types
export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone_number: string | null;
  is_phone_verified: boolean;
  is_email_verified: boolean;
  avatar: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  password: string;
  password_confirm: string;
}

// KYC types
export type KYCStatus =
  | "pending"
  | "processing"
  | "approved"
  | "rejected"
  | "resubmit_required";

export interface KYCDocument {
  id: string;
  document_type: string;
  file: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  is_verified: boolean;
  created_at: string;
}

export interface KYCLog {
  id: string;
  action: string;
  previous_status: string;
  new_status: string;
  performed_by_email: string | null;
  details: Record<string, unknown>;
  created_at: string;
}

export interface KYCApplication {
  id: string;
  user_email: string;
  user_full_name: string;
  status: KYCStatus;
  date_of_birth: string | null;
  nationality: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  kyc_provider_ref: string;
  kyc_provider_status: string;
  kyc_score: number | null;
  rejection_reason: string;
  admin_notes: string;
  submitted_at: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
  documents: KYCDocument[];
  logs: KYCLog[];
}

// Notification types
export interface Notification {
  id: string;
  channel: "email" | "sms" | "whatsapp" | "push" | "in_app";
  subject: string;
  message: string;
  status: "pending" | "sent" | "failed" | "read";
  is_read: boolean;
  created_at: string;
  sent_at: string | null;
  read_at: string | null;
}

// Pagination
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  total_pages: number;
  current_page: number;
  results: T[];
}
