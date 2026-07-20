import { api } from '@/lib/axios'
import type { PaginatedData, APIResponse } from '@/shared/types/api.types'
import type { DriverResponseDto, DriverCreateDto, DriverUpdateDto } from '../types/driver.types'

export const driverApi = {
  list: async (params?: {
    page?: number
    size?: number
    q?: string
    status?: string
    sort_by?: string
    order?: string
    include_deleted?: boolean
  }): Promise<PaginatedData<DriverResponseDto>> => {
    const response = await api.get<APIResponse<PaginatedData<DriverResponseDto>>>('/drivers', { params })
    return response.data.data
  },

  get: async (id: string): Promise<DriverResponseDto> => {
    const response = await api.get<APIResponse<DriverResponseDto>>(`/drivers/${id}`)
    return response.data.data
  },

  create: async (data: DriverCreateDto): Promise<DriverResponseDto> => {
    const response = await api.post<APIResponse<DriverResponseDto>>('/drivers', data)
    return response.data.data
  },

  update: async (id: string, data: DriverUpdateDto): Promise<DriverResponseDto> => {
    const response = await api.put<APIResponse<DriverResponseDto>>(`/drivers/${id}`, data)
    return response.data.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete<APIResponse<null>>(`/drivers/${id}`)
  },

  updateStatus: async (id: string, isActive: boolean): Promise<DriverResponseDto> => {
    const response = await api.patch<APIResponse<DriverResponseDto>>(
      `/drivers/${id}/status`,
      null,
      { params: { is_active: isActive } }
    )
    return response.data.data
  },
}
