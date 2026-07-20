import type { ReactNode } from 'react'
import { useAuthStore } from '@/stores/auth-store'

interface PermissionGuardProps {
  permission?: string
  permissions?: string[]
  mode?: 'any' | 'all'
  children: ReactNode
  fallback?: ReactNode
}

export function PermissionGuard({
  permission,
  permissions,
  mode = 'any',
  children,
  fallback = null,
}: PermissionGuardProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, isInitialized } = useAuthStore()

  if (!isInitialized) {
    return null // Do not evaluate until stores are loaded
  }

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
    console.debug(`[PermissionGuard] Access denied. Required: ${permission || permissions?.join(', ')} (Mode: ${mode})`)
    return <>{fallback}</>
  }

  return <>{children}</>
}
