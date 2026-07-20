import { LoginForm } from '../components/login-form'

export default function LoginPage() {
  return (
    <div className="flex flex-col space-y-2 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">
        Welcome back
      </h1>
      <p className="text-sm text-muted-foreground pb-6">
        Enter your credentials to access the TTMS dashboard.
      </p>
      <div className="text-left">
        <LoginForm />
      </div>
    </div>
  )
}
