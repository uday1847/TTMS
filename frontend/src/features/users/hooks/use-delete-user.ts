import { useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api'
import { useNotificationStore } from '@/stores/notification-store'

export function useDeleteUser() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: (id: string) => usersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      addNotification({ title: 'Success', message: 'User deleted successfully.', type: 'success' })
    },
  })
}
