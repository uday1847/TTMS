import { create } from 'zustand'

export type Theme = 'dark' | 'light' | 'system'

interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
}

export const useThemeStore = create<ThemeState>((set) => ({
  theme: (localStorage.getItem('ttms-theme') as Theme) || 'system',
  setTheme: (theme) => {
    localStorage.setItem('ttms-theme', theme)
    set({ theme })
  },
}))
