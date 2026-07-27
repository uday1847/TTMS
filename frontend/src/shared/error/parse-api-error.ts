import { AxiosError } from 'axios';
import type { ApiError } from './api-error';

export function parseApiError(error: unknown): ApiError {
  // If it's already an ApiError (from previous interceptor passes or custom throws)
  if (error && typeof error === 'object' && 'message' in error && 'raw' in error) {
    return error as ApiError;
  }

  if (error instanceof AxiosError) {
    const data = error.response?.data as any;
    const status = error.response?.status;
    const raw = error;

    if (!error.response) {
      if (error.code === 'ERR_NETWORK') {
        return { message: 'Network error. Please check your connection.', status, raw };
      }
      if (error.code === 'ECONNABORTED') {
        return { message: 'Request timed out.', status, raw };
      }
      return { message: error.message || 'An unexpected API error occurred.', status, raw };
    }

    // 1. FastAPI Validation Error (422 Unprocessable Entity)
    if (status === 422 && data?.detail && Array.isArray(data.detail)) {
      const errors: Record<string, string[]> = {};
      const messageParts: string[] = [];
      data.detail.forEach((err: any) => {
        const field = err.loc?.slice(1).join('.') || 'form';
        if (!errors[field]) errors[field] = [];
        errors[field].push(err.msg);
        messageParts.push(`${field}: ${err.msg}`);
      });
      const message = messageParts.length > 0 ? messageParts.join(', ') : 'Validation Error';
      return { message, status, errors, raw };
    }

    // 2. Custom TTMS API Envelope (Domain Exceptions)
    if (data?.message && typeof data.message === 'string') {
      return { 
        message: data.message, 
        status, 
        success: data.success, 
        code: data.code, 
        raw 
      };
    }

    // 3. Standard FastAPI HTTP Exception (400, 401, 403, 404, etc.)
    if (data?.detail && typeof data.detail === 'string') {
      return { message: data.detail, status, raw };
    }

    // 4. Fallback for unhandled HTTP errors
    return { message: error.message || `Request failed with status code ${status}`, status, raw };
  }

  if (error instanceof Error) {
    return { message: error.message, raw: error };
  }

  return { message: 'An unknown error occurred.', raw: error };
}
