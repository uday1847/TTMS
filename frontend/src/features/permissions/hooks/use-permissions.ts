import { useQuery } from '@tanstack/react-query'
import { permissionsApi } from '../api'

export function usePermissions() {
  return useQuery({
    queryKey: ['permissions'],
    queryFn: () => permissionsApi.list(),
  })
}
