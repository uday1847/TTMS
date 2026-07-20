import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface CurrentUser {
  id: string
  email: string
  username: string
}

interface AuthState {
  // Persisted state
  accessToken: string | null
  refreshToken: string | null
  expiresIn: number | null
  
  // Ephemeral state (hydrated from JWT)
  currentUser: CurrentUser | null
  roles: Set<string>
  permissions: Set<string>
  isAuthenticated: boolean
  isInitialized: boolean

  // Actions
  setTokens: (accessToken: string, refreshToken: string, expiresIn: number) => void
  hydrateFromJWT: (payload: any) => void
  clearAuth: () => void
  
  // Helpers
  hasPermission: (permission: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
  hasRole: (role: string) => boolean
  hasAnyRole: (roles: string[]) => boolean
  hasAllRoles: (roles: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      accessToken: null,
      refreshToken: null,
      expiresIn: null,
      
      currentUser: null,
      roles: new Set(),
      permissions: new Set(),
      isAuthenticated: false,
      isInitialized: false,

      // Set tokens immediately (e.g. on login response)
      setTokens: (accessToken, refreshToken, expiresIn) => 
        set({ accessToken, refreshToken, expiresIn }),
        
      // Hydrate everything from JWT
      hydrateFromJWT: (payload) => {
        set({
          currentUser: {
            id: payload.sub,
            email: payload.email,
            username: payload.email.split('@')[0], // fallback if username not in token
          },
          roles: new Set(payload.roles || []),
          permissions: new Set(payload.permissions || []),
          isAuthenticated: true,
          isInitialized: true,
        })
      },
      
      // Logout / Clear
      clearAuth: () => 
        set({
          accessToken: null,
          refreshToken: null,
          expiresIn: null,
          currentUser: null,
          roles: new Set(),
          permissions: new Set(),
          isAuthenticated: false,
          isInitialized: true, // Marked as initialized so the router knows we're done checking
        }),

      // Permission Helpers
      hasPermission: (permission) => get().permissions.has(permission),
      hasAnyPermission: (permissions) => permissions.some(p => get().permissions.has(p)),
      hasAllPermissions: (permissions) => permissions.every(p => get().permissions.has(p)),
      
      // Role Helpers
      hasRole: (role) => get().roles.has(role),
      hasAnyRole: (roles) => roles.some(r => get().roles.has(r)),
      hasAllRoles: (roles) => roles.every(r => get().roles.has(r)),
    }),
    {
      name: 'ttms-auth',
      // Only persist the tokens. The rest is transient and rebuilt on app load.
      partialize: (state) => ({ 
        accessToken: state.accessToken, 
        refreshToken: state.refreshToken, 
        expiresIn: state.expiresIn 
      }),
    }
  )
)
