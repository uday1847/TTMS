import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getTractors,
  getTractor,
  createTractor,
  updateTractor,
  updateTractorStatus,
  deleteTractor,
} from '../api/tractor.api';
import type { CreateTractorDto, UpdateTractorDto } from '../types/tractor.types';

export const tractorKeys = {
  all: ['tractors'] as const,
  lists: () => [...tractorKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...tractorKeys.lists(), filters] as const,
  details: () => [...tractorKeys.all, 'detail'] as const,
  detail: (id: string) => [...tractorKeys.details(), id] as const,
};

export function useTractors(params: Parameters<typeof getTractors>[0]) {
  return useQuery({
    queryKey: tractorKeys.list(params),
    queryFn: () => getTractors(params),
    placeholderData: (previousData) => previousData,
  });
}

export function useTractor(id: string) {
  return useQuery({
    queryKey: tractorKeys.detail(id),
    queryFn: () => getTractor(id),
    enabled: !!id,
  });
}

export function useCreateTractor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTractorDto) => createTractor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tractorKeys.lists() });
    },
  });
}

export function useUpdateTractor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTractorDto }) => updateTractor(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: tractorKeys.lists() });
      queryClient.invalidateQueries({ queryKey: tractorKeys.detail(variables.id) });
    },
  });
}

export function useUpdateTractorStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      updateTractorStatus(id, isActive),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: tractorKeys.lists() });
      queryClient.invalidateQueries({ queryKey: tractorKeys.detail(variables.id) });
    },
  });
}

export function useDeleteTractor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteTractor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tractorKeys.lists() });
    },
  });
}
