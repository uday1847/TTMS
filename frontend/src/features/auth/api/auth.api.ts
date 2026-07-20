import { api } from '@/lib/axios'
import type { LoginFormData, ForgotPasswordFormData, ResetPasswordFormData, ChangePasswordFormData } from '../schemas/auth.schema'
import type { UserResponse } from '@/features/users/api'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user_id: string
}

export const authApi = {
  login: async (data: LoginFormData): Promise<LoginResponse> => {
    const payload = {
      username_or_email: data.email,
      password: data.password,
      device_fingerprint: null,
    }
    const response = await api.post<LoginResponse>('/auth/login', payload)
    return response.data
  },

  logout: async (): Promise<void> => {
    // Backend endpoint '/auth/logout' does not exist
    throw new Error("Backend endpoint '/auth/logout' is not implemented.")
  },

  getCurrentUser: async (): Promise<{ user: UserResponse; permissions: string[] }> => {
    // Backend endpoint '/users/me' does not exist
    throw new Error("Backend endpoint '/users/me' is not implemented.")
  },

  forgotPassword: async (_data: ForgotPasswordFormData): Promise<void> => {
    // Backend endpoint '/auth/forgot-password' does not exist
    throw new Error("Backend endpoint '/auth/forgot-password' is not implemented.")
  },

  resetPassword: async (_data: ResetPasswordFormData): Promise<void> => {
    // Backend endpoint '/auth/reset-password' does not exist
    throw new Error("Backend endpoint '/auth/reset-password' is not implemented.")
  },

  changePassword: async (data: ChangePasswordFormData): Promise<void> => {
    await api.put('/auth/change-password', data)
  },
}
