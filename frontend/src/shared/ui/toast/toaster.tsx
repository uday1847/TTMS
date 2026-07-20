import { useEffect } from 'react'
import { useNotificationStore, type AppNotification } from '@/stores/notification-store'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'

export function Toaster() {
  const { notifications, markAsRead } = useNotificationStore()

  // Render only unread notifications, max 5 at a time
  const activeNotifications = notifications.filter((n) => !n.read).slice(0, 5)

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {activeNotifications.map((notification) => (
        <Toast key={notification.id} notification={notification} onClose={() => markAsRead(notification.id)} />
      ))}
    </div>
  )
}

function Toast({ notification, onClose }: { notification: AppNotification; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose()
    }, 5000)
    return () => clearTimeout(timer)
  }, [onClose])

  const icons = {
    success: <CheckCircle className="h-5 w-5 text-green-500" />,
    error: <AlertCircle className="h-5 w-5 text-red-500" />,
    warning: <AlertTriangle className="h-5 w-5 text-yellow-500" />,
    info: <Info className="h-5 w-5 text-blue-500" />,
  }

  const bgColors = {
    success: 'bg-green-50 border-green-200 text-green-900 dark:bg-green-950 dark:border-green-900 dark:text-green-50',
    error: 'bg-red-50 border-red-200 text-red-900 dark:bg-red-950 dark:border-red-900 dark:text-red-50',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900 dark:bg-yellow-950 dark:border-yellow-900 dark:text-yellow-50',
    info: 'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-950 dark:border-blue-900 dark:text-blue-50',
  }

  return (
    <div
      className={`pointer-events-auto flex w-full max-w-sm rounded-lg border p-4 shadow-lg transition-all ${
        bgColors[notification.type]
      }`}
    >
      <div className="flex w-full gap-3">
        <div className="flex-shrink-0">{icons[notification.type]}</div>
        <div className="flex-1 space-y-1 overflow-hidden">
          <p className="text-sm font-semibold truncate">{notification.title}</p>
          {notification.message && <p className="text-sm opacity-90 break-words whitespace-pre-line">{notification.message}</p>}
        </div>
        <button
          onClick={onClose}
          className="flex-shrink-0 h-fit rounded-md p-1 opacity-70 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-current"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
