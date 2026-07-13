import { create } from 'zustand'

export type UserRole = 'Admin' | 'Operator'

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setCredentials: (credentials: { user: User; accessToken: string; refreshToken: string }) => void
  clearCredentials: () => void
  updateAccessToken: (token: string) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  setCredentials: ({ user, accessToken, refreshToken }) =>
    set({
      user,
      accessToken,
      refreshToken,
      isAuthenticated: true,
    }),
  clearCredentials: () =>
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    }),
  updateAccessToken: (token) =>
    set((state) => ({
      ...state,
      accessToken: token,
    })),
}))
