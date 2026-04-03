// Auth and entitlement types — v1.0.7

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  session_token: string;
  user_id: string;
  email: string;
  role: string;
}

export interface EntitlementResponse {
  user_id: string;
  license_status: string;
  expires_at: string | null;
  trading_enabled: boolean;
  allowed_features: string[];
  visible_panels: string[];
  visible_rules: string[];
  editable_rules: string[];
  blocked_reason_messages: string[];
}

export interface AdminUserSummary {
  user_id: string;
  email: string;
  role: string;
  is_active: boolean;
  last_login_at: string | null;
  license_status: string | null;
  trading_enabled: boolean;
}

export interface AdminSummaryResponse {
  online_user_count: number;
  total_user_count: number;
  active_bot_count: number;
  open_position_count: number;
  closed_position_count: number;
  blocked_trade_count: number;
  alert_count: number;
}

export interface AdminEntitlementUpdateRequest {
  license_status: string;
  expires_at: string | null;
  trading_enabled: boolean;
  allowed_features: string[];
  visible_panels: string[];
  visible_rules: string[];
  editable_rules: string[];
  blocked_reason_messages: string[];
}
