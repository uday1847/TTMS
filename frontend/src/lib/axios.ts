import axios, { AxiosError } from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { env } from '@/config/env'
import { useAuthStore } from '@/stores/auth-store'

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
    
    if (error.response?.status === 401 && !originalRequest._retry) {
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

        // Placeholder token refresh logic
        // production flow:
        // const response = await axios.post(`${env.VITE_API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
        // const { access_token, refresh_token } = response.data
        const newAccessToken = 'refreshed-access-token'
        
        useAuthStore.getState().updateAccessToken(newAccessToken)
        
        processQueue(null, newAccessToken)
        isRefreshing = false

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        }
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        isRefreshing = false
        useAuthStore.getState().clearCredentials()
        return Promise.reject(refreshError)
      }
    }

    const apiError = {
      message: (error.response?.data as { detail?: string | { msg?: string }[] })?.detail 
        ? (typeof (error.response?.data as { detail: any }).detail === 'string' 
            ? (error.response?.data as { detail: string }).detail 
            : 'Validation error in request parameters')
        : error.message || 'An unexpected error occurred',
      status: error.response?.status,
      raw: error,
    }

    return Promise.reject(apiError)
  }
)
