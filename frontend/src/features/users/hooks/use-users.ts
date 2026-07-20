import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { usersApi } from '../api'

export function useUsers(params: { page?: number; size?: number; q?: string } = {}) {
  return useQuery({
    queryKey: ['users', params],
    queryFn: () => usersApi.list(params),
    placeholderData: keepPreviousData,
  })
}
