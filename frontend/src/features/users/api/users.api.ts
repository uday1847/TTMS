import { api } from '@/lib/axios'
import type { PaginatedData, APIResponse } from '@/shared/types/api.types'
import type { UserResponse, UserCreate, UserUpdate } from './users.types'

export const usersApi = {
  list: async (params?: { page?: number; size?: number; q?: string }): Promise<PaginatedData<UserResponse>> => {
    const response = await api.get<APIResponse<PaginatedData<UserResponse>>>('/users', { params })
    return response.data.data
  },

  get: async (id: string): Promise<UserResponse> => {
    const response = await api.get<APIResponse<UserResponse>>(`/users/${id}`)
    return response.data.data
  },

  create: async (data: UserCreate): Promise<UserResponse> => {
    const response = await api.post<APIResponse<UserResponse>>('/users', data)
    return response.data.data
  },

  update: async (id: string, data: UserUpdate): Promise<UserResponse> => {
    const response = await api.put<APIResponse<UserResponse>>(`/users/${id}`, data)
    return response.data.data
  },

  patch: async (id: string, data: UserUpdate): Promise<UserResponse> => {
    const response = await api.patch<APIResponse<UserResponse>>(`/users/${id}`, data)
    return response.data.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete<APIResponse<null>>(`/users/${id}`)
  },

  assignRole: async (id: string, roleName: string): Promise<UserResponse> => {
    const response = await api.post<APIResponse<UserResponse>>(`/users/${id}/roles/${roleName}`)
    return response.data.data
  },

  removeRole: async (id: string, roleName: string): Promise<UserResponse> => {
    const response = await api.delete<APIResponse<UserResponse>>(`/users/${id}/roles/${roleName}`)
    return response.data.data
  },

  getAccessProfile: async (id: string): Promise<UserResponse> => {
    const response = await api.get<APIResponse<UserResponse>>(`/users/${id}/access-profile`)
    return response.data.data
  },

  updateRoles: async (id: string, data: { roleIds: string[] }): Promise<UserResponse> => {
    const response = await api.put<APIResponse<UserResponse>>(`/users/${id}/roles`, data)
    return response.data.data
  },

  updatePermissionOverrides: async (id: string, data: { grantPermissions: string[], revokePermissions: string[] }): Promise<UserResponse> => {
    const response = await api.put<APIResponse<UserResponse>>(`/users/${id}/permissions`, data)
    return response.data.data
  },

  getEffectivePermissions: async (id: string): Promise<string[]> => {
    const response = await api.get<APIResponse<string[]>>(`/users/${id}/effective-permissions`)
    return response.data.data
  },
}
