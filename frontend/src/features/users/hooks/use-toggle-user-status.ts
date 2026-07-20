import { useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api'
import { useNotificationStore } from '@/stores/notification-store'

export function useToggleUserStatus() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) => usersApi.patch(id, { isActive }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      queryClient.invalidateQueries({ queryKey: ['user', data.id] })
      addNotification({ title: 'Success', message: `User status updated successfully.`, type: 'success' })
    },
    onError: (error: any) => {
      addNotification({ title: 'Error', message: error.message || 'Failed to update user status.', type: 'error' })
    },
  })
}
