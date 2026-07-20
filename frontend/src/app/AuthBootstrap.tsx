import { useEffect } from 'react'
import { useAuthStore } from '@/stores/auth-store'
import { decodeJWT, isTokenValid } from '@/utils/jwt.utils'

/**
 * AuthBootstrap mounts at the root of the application.
 * It is responsible for parsing the persisted accessToken and hydrating
 * the ephemeral state (currentUser, roles, permissions) before the router evaluates any protected routes.
 */
export function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const { accessToken, hydrateFromJWT, clearAuth, isInitialized } = useAuthStore()

  useEffect(() => {
    // If already initialized, do nothing
    if (isInitialized) return

    if (!accessToken) {
      console.debug('[AuthBootstrap] No access token found. Clearing auth state.')
      clearAuth()
      return
    }

    if (!isTokenValid(accessToken)) {
      console.debug('[AuthBootstrap] Access token is invalid or expired. Clearing auth state.')
      clearAuth()
      return
    }

    try {
      const payload = decodeJWT(accessToken)
      if (payload) {
        console.debug('[AuthBootstrap] Successfully decoded JWT. Hydrating auth store.')
        hydrateFromJWT(payload)
      } else {
        clearAuth()
      }
    } catch (err) {
      console.error('[AuthBootstrap] Failed to parse JWT:', err)
      clearAuth()
    }
  }, [accessToken, hydrateFromJWT, clearAuth, isInitialized])

  // While checking, render a loader to prevent premature routing decisions
  if (!isInitialized) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-muted-foreground animate-pulse text-sm">Initializing Secure Session...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
