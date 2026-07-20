import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema, type LoginFormData } from '../schemas/auth.schema'
import { useAuth } from '../hooks/use-auth'
import { Button } from '@/shared/ui/button/button'
import { Input } from '@/shared/ui/input/input'
import { Link } from 'react-router'
import { Loader2 } from 'lucide-react'

export function LoginForm() {
  const { login, isLoggingIn } = useAuth()
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const onSubmit = async (data: LoginFormData) => {
    await login(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            Email
          </label>
          <Input
            id="email"
            type="email"
            placeholder="admin@ttms.com"
            {...register('email')}
            disabled={isLoggingIn}
            className={errors.email ? 'border-destructive' : ''}
          />
          {errors.email && (
            <p className="text-[0.8rem] font-medium text-destructive">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              Password
            </label>
            <Link
              to="/forgot-password"
              className="text-sm font-medium text-primary hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <Input
            id="password"
            type="password"
            {...register('password')}
            disabled={isLoggingIn}
            className={errors.password ? 'border-destructive' : ''}
          />
          {errors.password && (
            <p className="text-[0.8rem] font-medium text-destructive">{errors.password.message}</p>
          )}
        </div>

        {/* Remember me removed to match backend LoginRequest DTO */}
      </div>

      <Button type="submit" className="w-full" disabled={isLoggingIn}>
        {isLoggingIn ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Signing in...
          </>
        ) : (
          'Sign in'
        )}
      </Button>
    </form>
  )
}
