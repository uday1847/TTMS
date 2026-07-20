import { useQuery } from '@tanstack/react-query'
import { usersApi } from '../api'

export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => usersApi.get(id),
    enabled: !!id,
  })
}
