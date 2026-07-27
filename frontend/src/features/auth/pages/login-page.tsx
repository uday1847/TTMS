import { useSearchParams } from 'react-router'
import { LoginForm } from '../components/login-form'
import { ShieldAlert } from 'lucide-react'

export default function LoginPage() {
  const [searchParams] = useSearchParams()
  const reason = searchParams.get('reason')

  return (
    <div className="flex flex-col space-y-2 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">
        Welcome back
      </h1>
      <p className="text-sm text-muted-foreground pb-6">
        Enter your credentials to access the TTMS dashboard.
      </p>
      
      {reason === 'security_update' && (
        <div className="mb-6 flex items-center gap-2 rounded-md bg-destructive/15 p-4 text-left text-sm text-destructive shadow-sm">
          <ShieldAlert className="h-5 w-5 shrink-0" />
          <p>
            Your session expired because your account permissions or security settings have changed. Please log in again.
          </p>
        </div>
      )}

      <div className="text-left">
        <LoginForm />
      </div>
    </div>
  )
}
