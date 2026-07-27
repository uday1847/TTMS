import { api } from '@/lib/axios';
import type { APIResponse as ApiResponse, PaginatedData } from '@/shared/types/api.types';
import type { 
  TripResponseDto, 
  TripCreateDto, 
  TripUpdateDto, 
  TripStatusUpdateDto, 
  TripStatusHistoryResponseDto 
} from '../types/trip.types';

export async function getTrips(params: Record<string, any>) {
  const response = await api.get<ApiResponse<PaginatedData<TripResponseDto>>>('/trips', { params });
  return response.data.data;
}

export async function getActiveTrips(params: Record<string, any>) {
  const response = await api.get<ApiResponse<PaginatedData<TripResponseDto>>>('/trips/active', { params });
  return response.data.data;
}

export async function getCompletedTrips(params: Record<string, any>) {
  const response = await api.get<ApiResponse<PaginatedData<TripResponseDto>>>('/trips/completed', { params });
  return response.data.data;
}

export async function getPendingTrips(params: Record<string, any>) {
  const response = await api.get<ApiResponse<PaginatedData<TripResponseDto>>>('/trips/pending', { params });
  return response.data.data;
}

export async function getTrip(id: string) {
  const response = await api.get<ApiResponse<TripResponseDto>>(`/trips/${id}`);
  return response.data.data;
}

export async function createTrip(data: TripCreateDto) {
  const response = await api.post<ApiResponse<TripResponseDto>>('/trips', data);
  return response.data.data;
}

export async function updateTrip(id: string, data: TripUpdateDto) {
  const response = await api.put<ApiResponse<TripResponseDto>>(`/trips/${id}`, data);
  return response.data.data;
}

export async function updateTripStatus(id: string, data: TripStatusUpdateDto) {
  const response = await api.patch<ApiResponse<TripResponseDto>>(`/trips/${id}/status`, data);
  return response.data.data;
}

export async function getTripHistory(id: string) {
  const response = await api.get<ApiResponse<TripStatusHistoryResponseDto[]>>(`/trips/${id}/history`);
  return response.data.data;
}

export async function deleteTrip(id: string) {
  const response = await api.delete<ApiResponse<null>>(`/trips/${id}`);
  return response.data.data;
}
