import { Navigate, Outlet, useLocation } from 'react-router'
import { useAuthStore } from '@/stores/auth-store'

export function PublicRoute() {
  const { isAuthenticated } = useAuthStore()
  const location = useLocation()

  if (isAuthenticated) {
    const from = location.state?.from?.pathname || '/dashboard'
    return <Navigate to={from} replace />
  }

  return <Outlet />
}
