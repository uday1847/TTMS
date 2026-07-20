import { AxiosError } from 'axios'

export interface ApiError {
  message: string
  status?: number
  errors?: Record<string, string[]>
}

export function parseApiError(error: unknown): ApiError {
  if (error && typeof error === 'object' && 'raw' in error && 'message' in error) {
    // Already formatted by interceptor
    return error as ApiError
  }

  if (error instanceof AxiosError) {
    const data = error.response?.data as any
    const status = error.response?.status

    // FastAPI Validation Error (422)
    if (status === 422 && data?.detail && Array.isArray(data.detail)) {
      const errors: Record<string, string[]> = {}
      const messageParts: string[] = []
      data.detail.forEach((err: any) => {
        const field = err.loc?.slice(1).join('.') || 'form'
        if (!errors[field]) errors[field] = []
        errors[field].push(err.msg)
        messageParts.push(`${field}: ${err.msg}`)
      })
      const message = messageParts.length > 0 ? messageParts.join(', ') : 'Validation Error'
      return { message, status, errors }
    }

    // Standard FastAPI Error (400, 401, 403, etc.)
    if (data?.detail && typeof data.detail === 'string') {
      return { message: data.detail, status }
    }

    return { message: error.message || 'An unexpected API error occurred.', status }
  }

  if (error instanceof Error) {
    return { message: error.message }
  }

  return { message: 'An unknown error occurred.' }
}
