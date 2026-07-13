import { Navigate, Outlet } from 'react-router'
import { useAuthStore } from '@/stores/auth-store'

export function AdminRoute() {
  const user = useAuthStore((state) => state.user)

  if (user?.role !== 'Admin') {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
