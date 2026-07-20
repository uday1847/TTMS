import { api } from '@/lib/axios'
import type { APIResponse } from '@/shared/types/api.types'
import type { RoleResponse, RoleCreate } from './roles.types'

export const rolesApi = {
  list: async (): Promise<RoleResponse[]> => {
    const response = await api.get<APIResponse<RoleResponse[]>>('/roles')
    return response.data.data
  },

  create: async (data: RoleCreate): Promise<RoleResponse> => {
    const response = await api.post<APIResponse<RoleResponse>>('/roles', data)
    return response.data.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete<APIResponse<null>>(`/roles/${id}`)
  },

  assignPermission: async (id: string, permissionCode: string): Promise<RoleResponse> => {
    const response = await api.post<APIResponse<RoleResponse>>(`/roles/${id}/permissions/${permissionCode}`)
    return response.data.data
  },

  removePermission: async (id: string, permissionCode: string): Promise<RoleResponse> => {
    const response = await api.delete<APIResponse<RoleResponse>>(`/roles/${id}/permissions/${permissionCode}`)
    return response.data.data
  },
}
