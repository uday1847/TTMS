import { Navigate, Outlet, useLocation } from 'react-router'
import { ErrorBoundary } from 'react-error-boundary'
import { useAuthStore } from '@/stores/auth-store'

function RouteErrorFallback({ error }: { error: any }) {
  return (
    <div className="p-6 bg-red-50 text-red-900 rounded-md border border-red-200 m-4">
      <h2 className="text-xl font-bold mb-2">Something went wrong in this page</h2>
      <pre className="text-sm overflow-auto whitespace-pre-wrap bg-red-100 p-4 rounded-md">{error?.message || 'Unknown error'}</pre>
      <pre className="text-xs overflow-auto whitespace-pre-wrap mt-2">{error?.stack}</pre>
    </div>
  );
}

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

  return (
    <ErrorBoundary FallbackComponent={RouteErrorFallback}>
      <Outlet />
    </ErrorBoundary>
  )
}
