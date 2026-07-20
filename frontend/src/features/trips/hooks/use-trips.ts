import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as tripApi from '../api/trip.api';
import type { 
  TripCreateDto, 
  TripUpdateDto, 
  TripStatusUpdateDto 
} from '../types/trip.types';

export const tripKeys = {
  all: ['trips'] as const,
  lists: () => [...tripKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...tripKeys.lists(), { filters }] as const,
  details: () => [...tripKeys.all, 'detail'] as const,
  detail: (id: string) => [...tripKeys.details(), id] as const,
  history: (id: string) => [...tripKeys.detail(id), 'history'] as const,
};

export function useTrips(filters: Record<string, any>) {
  return useQuery({
    queryKey: tripKeys.list(filters),
    queryFn: () => tripApi.getTrips(filters),
  });
}

export function useActiveTrips(filters: Record<string, any>) {
  return useQuery({
    queryKey: [...tripKeys.lists(), 'active', { filters }],
    queryFn: () => tripApi.getActiveTrips(filters),
  });
}

export function useCompletedTrips(filters: Record<string, any>) {
  return useQuery({
    queryKey: [...tripKeys.lists(), 'completed', { filters }],
    queryFn: () => tripApi.getCompletedTrips(filters),
  });
}

export function usePendingTrips(filters: Record<string, any>) {
  return useQuery({
    queryKey: [...tripKeys.lists(), 'pending', { filters }],
    queryFn: () => tripApi.getPendingTrips(filters),
  });
}

export function useTrip(id: string) {
  return useQuery({
    queryKey: tripKeys.detail(id),
    queryFn: () => tripApi.getTrip(id),
    enabled: !!id,
  });
}

export function useTripHistory(id: string) {
  return useQuery({
    queryKey: tripKeys.history(id),
    queryFn: () => tripApi.getTripHistory(id),
    enabled: !!id,
  });
}

export function useCreateTrip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TripCreateDto) => tripApi.createTrip(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tripKeys.all });
    },
  });
}

export function useUpdateTrip(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TripUpdateDto) => tripApi.updateTrip(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tripKeys.all });
    },
  });
}

export function useUpdateTripStatus(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TripStatusUpdateDto) => tripApi.updateTripStatus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tripKeys.all });
    },
  });
}

export function useDeleteTrip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => tripApi.deleteTrip(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tripKeys.all });
    },
  });
}
