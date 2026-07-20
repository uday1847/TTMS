import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { forgotPasswordSchema, type ForgotPasswordFormData } from '../schemas/auth.schema'
import { useAuth } from '../hooks/use-auth'
import { Button } from '@/shared/ui/button/button'
import { Input } from '@/shared/ui/input/input'
import { Link } from 'react-router'
import { Loader2 } from 'lucide-react'

export function ForgotPasswordForm() {
  const { forgotPassword, isSendingResetEmail } = useAuth()
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: '' },
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    await forgotPassword(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium leading-none">
            Email Address
          </label>
          <Input
            id="email"
            type="email"
            placeholder="admin@ttms.com"
            {...register('email')}
            disabled={isSendingResetEmail}
            className={errors.email ? 'border-destructive' : ''}
          />
          {errors.email && (
            <p className="text-[0.8rem] font-medium text-destructive">{errors.email.message}</p>
          )}
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={isSendingResetEmail}>
        {isSendingResetEmail ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Sending Reset Link...
          </>
        ) : (
          'Send Reset Link'
        )}
      </Button>

      <div className="text-center text-sm">
        Remember your password?{' '}
        <Link to="/login" className="font-medium text-primary hover:underline">
          Sign In
        </Link>
      </div>
    </form>
  )
}
