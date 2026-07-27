import { useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi, type UserCreate } from '../api'
import { useNotificationStore } from '@/stores/notification-store'

export function useCreateUser() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: (data: UserCreate) => usersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      addNotification({ title: 'Success', message: 'User created successfully.', type: 'success' })
    },
  })
}
