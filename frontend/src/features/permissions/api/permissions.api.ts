import { api } from '@/lib/axios'
import type { APIResponse } from '@/shared/types/api.types'
import type { PermissionResponse } from './permissions.types'

export const permissionsApi = {
  list: async (): Promise<PermissionResponse[]> => {
    const response = await api.get<APIResponse<PermissionResponse[]>>('/permissions')
    return response.data.data
  },
}
