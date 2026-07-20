import type { ReactNode } from 'react'
import { useAuthStore } from '@/stores/auth-store'

interface RoleGuardProps {
  role?: string
  roles?: string[]
  mode?: 'any' | 'all'
  children: ReactNode
  fallback?: ReactNode
}

export function RoleGuard({
  role,
  roles,
  mode = 'any',
  children,
  fallback = null,
}: RoleGuardProps) {
  const { hasRole, hasAnyRole, hasAllRoles, isInitialized } = useAuthStore()

  if (!isInitialized) {
    return null // Do not evaluate until stores are loaded
  }

  let isAllowed = true

  if (role) {
    isAllowed = hasRole(role)
  } else if (roles && roles.length > 0) {
    if (mode === 'all') {
      isAllowed = hasAllRoles(roles)
    } else {
      isAllowed = hasAnyRole(roles)
    }
  }

  if (!isAllowed) {
    console.debug(`[RoleGuard] Access denied. Required: ${role || roles?.join(', ')} (Mode: ${mode})`)
    return <>{fallback}</>
  }

  return <>{children}</>
}
