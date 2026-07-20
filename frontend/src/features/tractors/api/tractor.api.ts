import { api } from '@/api/axios';
import type { APIResponse, PaginatedData } from '@/shared/types/api.types';
import type {
  TractorResponseDto,
  CreateTractorDto,
  UpdateTractorDto,
} from '../types/tractor.types';

export async function getTractors(params: {
  page?: number;
  size?: number;
  q?: string;
  status?: string;
  insurance_expiring_days?: number;
  created_date_start?: string;
  created_date_end?: string;
  sort_by?: string;
  order?: string;
  include_deleted?: boolean;
}): Promise<PaginatedData<TractorResponseDto>> {
  const response = await api.get<APIResponse<PaginatedData<TractorResponseDto>>>('/tractors', {
    params,
  });
  return response.data.data;
}

export async function getTractor(id: string): Promise<TractorResponseDto> {
  const response = await api.get<APIResponse<TractorResponseDto>>(`/tractors/${id}`);
  return response.data.data;
}

export async function createTractor(data: CreateTractorDto): Promise<TractorResponseDto> {
  const response = await api.post<APIResponse<TractorResponseDto>>('/tractors', data);
  return response.data.data;
}

export async function updateTractor(id: string, data: UpdateTractorDto): Promise<TractorResponseDto> {
  const response = await api.put<APIResponse<TractorResponseDto>>(`/tractors/${id}`, data);
  return response.data.data;
}

export async function updateTractorStatus(id: string, isActive: boolean): Promise<TractorResponseDto> {
  const response = await api.patch<APIResponse<TractorResponseDto>>(`/tractors/${id}/status`, null, {
    params: { is_active: isActive },
  });
  return response.data.data;
}

export async function deleteTractor(id: string): Promise<void> {
  await api.delete<APIResponse<null>>(`/tractors/${id}`);
}
