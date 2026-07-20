import { Navigate, Outlet, useLocation } from 'react-router'
import { useAuthStore } from '@/stores/auth-store'

interface ProtectedRouteProps {
  permission?: string
  permissions?: string[]
  mode?: 'any' | 'all'
}

export function ProtectedRoute({ permission, permissions, mode = 'any' }: ProtectedRouteProps) {
  const { isAuthenticated, isInitialized, hasPermission, hasAnyPermission, hasAllPermissions } = useAuthStore()
  const location = useLocation()

  // Wait until AuthBootstrap finishes hydrating the store
  if (!isInitialized) {
    return null
  }

  // Not authenticated? Send to login.
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check permissions if provided
  let isAllowed = true

  if (permission) {
    isAllowed = hasPermission(permission)
  } else if (permissions && permissions.length > 0) {
    if (mode === 'all') {
      isAllowed = hasAllPermissions(permissions)
    } else {
      isAllowed = hasAnyPermission(permissions)
    }
  }

  if (!isAllowed) {
    console.debug(`[ProtectedRoute] Access denied to ${location.pathname}. Required: ${permission || permissions?.join(', ')} (Mode: ${mode})`)
    return <Navigate to="/unauthorized" replace />
  }

  return <Outlet />
}
