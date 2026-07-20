import { create } from 'zustand'

interface LoadingState {
  globalLoading: boolean
  setGlobalLoading: (isLoading: boolean) => void
  loaders: Record<string, boolean>
  setLoader: (key: string, isLoading: boolean) => void
}

export const useLoadingStore = create<LoadingState>((set) => ({
  globalLoading: false,
  setGlobalLoading: (isLoading) => set({ globalLoading: isLoading }),
  loaders: {},
  setLoader: (key, isLoading) =>
    set((state) => ({
      loaders: {
        ...state.loaders,
        [key]: isLoading,
      },
    })),
}))
