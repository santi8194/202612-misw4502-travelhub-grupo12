export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
}

export interface ConfirmRegistrationRequest {
  email: string;
  code: string;
}

export interface AuthTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
