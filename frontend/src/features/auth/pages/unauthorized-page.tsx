import { Link } from 'react-router'
import { Button } from '@/shared/ui/button/button'
import { ShieldAlert } from 'lucide-react'

export default function UnauthorizedPage() {
  return (
    <div className="flex h-screen w-full flex-col items-center justify-center bg-background text-foreground">
      <ShieldAlert className="h-24 w-24 text-destructive mb-6" />
      <h1 className="text-4xl font-bold tracking-tight mb-2">Access Denied</h1>
      <p className="text-muted-foreground mb-8 text-center max-w-md">
        You do not have the required permissions to view this page. If you believe this is an error, please contact your administrator.
      </p>
      <Button asChild>
        <Link to="/dashboard">Return to Dashboard</Link>
      </Button>
    </div>
  )
}
