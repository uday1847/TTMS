import { useQuery } from '@tanstack/react-query'
import { rolesApi } from '../api'

export function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: () => rolesApi.list(),
  })
}
