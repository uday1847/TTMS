import { create } from 'zustand'

export interface AppNotification {
  id: string
  title: string
  message?: string
  type: 'success' | 'error' | 'warning' | 'info'
  read: boolean
  createdAt: Date
}

interface NotificationState {
  notifications: AppNotification[]
  addNotification: (notification: Omit<AppNotification, 'id' | 'read' | 'createdAt'>) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  clearNotifications: () => void
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        {
          ...notification,
          id: crypto.randomUUID(),
          read: false,
          createdAt: new Date(),
        },
        ...state.notifications,
      ],
    })),
  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
    })),
  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    })),
  clearNotifications: () => set({ notifications: [] }),
}))
