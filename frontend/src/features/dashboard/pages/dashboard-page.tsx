import { Link } from 'react-router'
import { PermissionGuard } from '@/shared/auth'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">TTMS Central Logistics Overview</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Placeholder cards for structural visual preview */}
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-xl border bg-card p-6 shadow-sm">
            <div className="h-4 w-24 bg-muted rounded mb-2 animate-pulse"></div>
            <div className="h-8 w-16 bg-muted rounded animate-pulse"></div>
          </div>
        ))}
      </div>

      <div>
        <h2 className="text-xl font-semibold tracking-tight mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <PermissionGuard permission="users:read">
            <Link
              to="/users"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium h-10 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Manage Users
            </Link>
          </PermissionGuard>
          <PermissionGuard permission="drivers:read">
            <Link
              to="/drivers"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium h-10 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Manage Drivers
            </Link>
          </PermissionGuard>
        </div>
      </div>
    </div>
  )
}
