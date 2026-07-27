import { api } from '@/lib/axios';
import type { APIResponse as ApiResponse, PaginatedData } from '@/shared/types/api.types';
import type { PartyResponseDto, PartyCreateDto, PartyUpdateDto } from '../types/party.types';

export const partyApi = {
  getParties: async (filters: Record<string, any> = {}) => {
    const { data } = await api.get<ApiResponse<PaginatedData<PartyResponseDto>>>('/parties', { params: filters });
    return data.data;
  },

  getParty: async (id: string) => {
    const { data } = await api.get<ApiResponse<PartyResponseDto>>(`/parties/${id}`);
    return data.data;
  },

  createParty: async (payload: PartyCreateDto) => {
    const { data } = await api.post<ApiResponse<PartyResponseDto>>('/parties', payload);
    return data.data;
  },

  updateParty: async (id: string, payload: PartyUpdateDto) => {
    const { data } = await api.put<ApiResponse<PartyResponseDto>>(`/parties/${id}`, payload);
    return data.data;
  },

  deleteParty: async (id: string) => {
    const { data } = await api.delete<ApiResponse<null>>(`/parties/${id}`);
    return data.data;
  },

  updatePartyStatus: async (id: string, isActive: boolean) => {
    const { data } = await api.patch<ApiResponse<PartyResponseDto>>(`/parties/${id}/status`, null, {
      params: { is_active: isActive }
    });
    return data.data;
  }
};
