import { Outlet } from 'react-router'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen w-screen items-center justify-center bg-muted/10 px-4 py-12 dark:bg-background">
      <div className="w-full max-w-md space-y-8 bg-card p-8 border rounded-lg shadow-sm">
        <Outlet />
      </div>
    </div>
  )
}
