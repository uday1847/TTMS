import { create } from 'zustand'
import type { ApiError } from '@/shared/utils/api-error'

interface GlobalErrorState {
  error: ApiError | null
  hasError: boolean
  setError: (error: ApiError | null) => void
  clearError: () => void
}

export const useErrorStore = create<GlobalErrorState>((set) => ({
  error: null,
  hasError: false,
  setError: (error) => set({ error, hasError: !!error }),
  clearError: () => set({ error: null, hasError: false }),
}))
