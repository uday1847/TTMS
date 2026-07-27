import { useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi, type UserUpdate } from '../api'
import { useNotificationStore } from '@/stores/notification-store'

export function useUpdateUser() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UserUpdate }) => usersApi.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      queryClient.invalidateQueries({ queryKey: ['user', data.id] })
      addNotification({ title: 'Success', message: 'User updated successfully.', type: 'success' })
    },
  })
}
