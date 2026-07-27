import axios, { AxiosError } from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { env } from '@/config/env'
import { useAuthStore } from '@/stores/auth-store'
import { parseApiError } from '@/shared/error';
import { decodeJWT } from '@/utils/jwt.utils'
import { queryClient } from '@/lib/query-client'

export const api = axios.create({
  baseURL: env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Response interceptor to handle token refresh and standard errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    const isAuthEndpoint = originalRequest.url?.includes('/auth/login') || 
                           originalRequest.url?.includes('/auth/refresh') || 
                           originalRequest.url?.includes('/auth/forgot-password') || 
                           originalRequest.url?.includes('/auth/reset-password')

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      // Check for security invalidation
      if ((error.response.data as any)?.detail === "Your permissions or account security settings have changed. Please log in again.") {
        const authStore = useAuthStore.getState()
        authStore.clearAuth()
        queryClient.clear()
        
        // Notify other tabs
        const channel = new BroadcastChannel('auth_sync')
        channel.postMessage({ type: 'LOGOUT' })
        channel.close()
        
        window.location.href = '/login?reason=security_update'
        return Promise.reject(parseApiError(error))
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return api(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = useAuthStore.getState().refreshToken
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        const response = await axios.post(`${env.VITE_API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
        const newAccessToken = response.data.access_token
        const newRefreshToken = response.data.refresh_token // Assume new refresh token is issued

        const store = useAuthStore.getState()
        store.setTokens(
          newAccessToken,
          newRefreshToken || refreshToken,
          response.data.expires_in || store.expiresIn || 3600
        )
        
        // Re-hydrate ephemeral state from new token
        const payload = decodeJWT(newAccessToken)
        if (payload) {
          store.hydrateFromJWT(payload)
        }

        processQueue(null, newAccessToken)
        isRefreshing = false

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        }
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        isRefreshing = false
        useAuthStore.getState().clearAuth()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(parseApiError(error))
  }
)
