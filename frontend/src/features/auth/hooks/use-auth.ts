import { useMutation } from '@tanstack/react-query'
import { authApi } from '../api/auth.api'
import { useAuthStore } from '@/stores/auth-store'
import { useNotificationStore } from '@/stores/notification-store'
import { showApiError } from '@/shared/error'
import { useNavigate } from 'react-router'
import type { LoginFormData, ForgotPasswordFormData, ResetPasswordFormData, ChangePasswordFormData } from '../schemas/auth.schema'

import { decodeJWT } from '@/utils/jwt.utils'

export function useAuth() {
  const navigate = useNavigate()
  const { setTokens, hydrateFromJWT, clearAuth } = useAuthStore()
  const { addNotification } = useNotificationStore()

  const loginMutation = useMutation({
    mutationFn: (data: LoginFormData) => authApi.login(data),
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token, data.expires_in)
      
      const payload = decodeJWT(data.access_token)
      if (payload) {
        hydrateFromJWT(payload)
      } else {
        console.error('Failed to decode JWT on login')
        clearAuth()
      }
      
      addNotification({
        title: 'Welcome back!',
        message: 'You have successfully logged in.',
        type: 'success',
      })
      
      navigate('/dashboard')
    },
    onError: (error: any) => {
      showApiError(error, 'Login Failed')
    },
  })

  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(),
    onError: (error: any) => {
      showApiError(error, 'Logout Notice')
    },
    onSettled: () => {
      clearAuth()
      navigate('/login')
    },
  })

  const forgotPasswordMutation = useMutation({
    mutationFn: (data: ForgotPasswordFormData) => authApi.forgotPassword(data),
    onSuccess: () => {
      addNotification({
        title: 'Email Sent',
        message: 'Check your inbox for password reset instructions.',
        type: 'success',
      })
    },
    onError: (error: any) => {
      showApiError(error, 'Error')
    },
  })

  const resetPasswordMutation = useMutation({
    mutationFn: (data: ResetPasswordFormData) => authApi.resetPassword(data),
    onSuccess: () => {
      addNotification({
        title: 'Password Reset',
        message: 'Your password has been successfully reset. You can now login.',
        type: 'success',
      })
      navigate('/login')
    },
    onError: (error: any) => {
      showApiError(error, 'Reset Failed')
    },
  })

  const changePasswordMutation = useMutation({
    mutationFn: (data: ChangePasswordFormData) => authApi.changePassword(data),
    onSuccess: () => {
      addNotification({
        title: 'Password Changed',
        message: 'Your password was updated successfully.',
        type: 'success',
      })
    },
    onError: (error: any) => {
      showApiError(error, 'Update Failed')
    },
  })

  return {
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
    forgotPassword: forgotPasswordMutation.mutateAsync,
    isSendingResetEmail: forgotPasswordMutation.isPending,
    resetPassword: resetPasswordMutation.mutateAsync,
    isResettingPassword: resetPasswordMutation.isPending,
    changePassword: changePasswordMutation.mutateAsync,
    isChangingPassword: changePasswordMutation.isPending,
  }
}
