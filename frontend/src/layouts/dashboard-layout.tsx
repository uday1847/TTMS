import { Outlet, Link } from 'react-router'
import { useSidebarStore } from '@/stores/sidebar-store'
import { useAuthStore } from '@/stores/auth-store'
import { useTheme } from '@/providers/theme-provider'
import { Menu, X, Sun, Moon, LogOut, LayoutDashboard, Truck, UserCheck, Shield, FileText, Settings } from 'lucide-react'

export function DashboardLayout() {
  const { isOpen, toggle } = useSidebarStore()
  const { user, clearCredentials } = useAuthStore()
  const { theme, setTheme } = useTheme()

  const handleLogout = () => {
    clearCredentials()
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex flex-col border-r bg-card transition-all duration-300 ${
          isOpen ? 'w-64' : 'w-16'
        } lg:static`}
      >
        <div className="flex h-16 items-center justify-between px-4 border-b">
          <Link to="/dashboard" className="flex items-center gap-2 font-bold text-lg overflow-hidden whitespace-nowrap">
            <LayoutDashboard className="h-6 w-6 text-primary flex-shrink-0" />
            {isOpen && <span>TTMS Portal</span>}
          </Link>
          <button onClick={toggle} className="p-1 rounded-md hover:bg-muted lg:hidden">
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 p-2 overflow-y-auto">
          <Link to="/dashboard" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-muted">
            <LayoutDashboard className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>Dashboard</span>}
          </Link>
          <Link to="/drivers" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-muted">
            <UserCheck className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>Drivers</span>}
          </Link>
          <Link to="/tractors" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-muted">
            <Truck className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>Tractors</span>}
          </Link>
          <Link to="/trips" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-muted">
            <FileText className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>Trips</span>}
          </Link>
          {user?.role === 'Admin' && (
            <Link to="/users" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-muted">
              <Shield className="h-5 w-5 flex-shrink-0" />
              {isOpen && <span>Admin Console</span>}
            </Link>
          )}
          <Link to="/settings" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-muted">
            <Settings className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>Settings</span>}
          </Link>
        </nav>

        <div className="p-4 border-t flex flex-col gap-2">
          {isOpen && (
            <div className="text-xs text-muted-foreground mb-1">
              Logged in as: <span className="font-semibold text-foreground">{user?.email || 'Guest'}</span>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-3 py-2 text-sm font-medium text-destructive hover:bg-destructive/10 rounded-md transition-colors"
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>Sign Out</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Pane */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b bg-card px-4 lg:px-6">
          <div className="flex items-center gap-4">
            <button onClick={toggle} className="p-1 rounded-md hover:bg-muted lg:block hidden">
              <Menu className="h-5 w-5" />
            </button>
            <button onClick={toggle} className="p-1 rounded-md hover:bg-muted lg:hidden">
              <Menu className="h-5 w-5" />
            </button>
            
            {/* Breadcrumb Placeholder */}
            <nav className="hidden sm:flex" aria-label="Breadcrumb">
              <ol className="flex items-center space-x-2 text-sm text-muted-foreground">
                <li>
                  <Link to="/dashboard" className="hover:text-foreground">Home</Link>
                </li>
                <li>/</li>
                <li className="font-medium text-foreground">Dashboard</li>
              </ol>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {/* Theme Toggle */}
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 bg-muted/10">
          <Outlet />
        </main>

        {/* Footer */}
        <footer className="border-t bg-card py-3 px-6 text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} TTMS Fleet Portal. All rights reserved.
        </footer>
      </div>
    </div>
  )
}
