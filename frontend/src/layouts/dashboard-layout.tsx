import { Outlet, NavLink, useNavigate, useLocation } from 'react-router'
import { useAuthStore } from '@/stores/auth-store'
import { useThemeStore } from '@/stores/theme-store'
import { Button } from '@/shared/ui/button/button'
import { Truck, LogOut, User as UserIcon, Moon, Sun } from 'lucide-react'
import { PermissionGuard } from '@/shared/auth'
import { PERMISSIONS } from '@/constants/permissions'

export function DashboardLayout() {
  const { clearAuth, currentUser, roles } = useAuthStore()
  const { theme, setTheme } = useThemeStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-md text-sm font-medium ${
      isActive ? 'bg-accent text-accent-foreground' : 'hover:bg-accent hover:text-accent-foreground'
    }`

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-card border-r border-border hidden md:flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <Truck className="h-6 w-6 text-primary mr-2" />
          <span className="font-bold text-lg tracking-tight">TTMS</span>
        </div>
        
        <nav className="flex-1 p-4 flex flex-col gap-2">
          <NavLink to="/dashboard" className={navLinkClass}>Dashboard</NavLink>
          
          <PermissionGuard permission={PERMISSIONS.TRIPS_READ}>
            <NavLink to="/trips" className={navLinkClass}>Trips</NavLink>
          </PermissionGuard>
          
          <PermissionGuard permission={PERMISSIONS.TRACTORS_READ}>
            <NavLink to="/tractors" className={navLinkClass}>Tractors</NavLink>
          </PermissionGuard>
          
          <PermissionGuard permission={PERMISSIONS.DRIVERS_READ}>
            <NavLink to="/drivers" className={navLinkClass}>Drivers</NavLink>
          </PermissionGuard>
          
          <NavLink to="/expenses" className={navLinkClass}>Expenses</NavLink>
          <NavLink to="/reports" className={navLinkClass}>Reports</NavLink>
          
          <PermissionGuard permission={PERMISSIONS.USERS_READ}>
            <NavLink to="/users" className={navLinkClass}>Users</NavLink>
          </PermissionGuard>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-border bg-card">
          <div className="flex items-center md:hidden">
            <Truck className="h-6 w-6 text-primary mr-2" />
            <span className="font-bold">TTMS</span>
          </div>

          <div className="hidden md:block">
            <h2 className="text-sm font-medium text-muted-foreground capitalize">
              Main / {location.pathname.split('/')[1] || 'Dashboard'}
            </h2>
          </div>
          
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
            
            <div className="flex items-center gap-2 border-l pl-4 border-border">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                <UserIcon className="h-4 w-4 text-primary" />
              </div>
              <div className="hidden sm:flex flex-col">
                <span className="text-sm font-medium leading-none">{currentUser?.username || 'User'}</span>
                <span className="text-xs text-muted-foreground">{Array.from(roles)[0] || 'Guest'}</span>
              </div>
              <Button variant="ghost" size="icon" onClick={handleLogout} title="Log out">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  )
}
