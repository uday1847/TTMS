import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { partyApi } from '../api/party.api';
import type { PartyCreateDto, PartyUpdateDto } from '../types/party.types';

export const partyKeys = {
  all: ['parties'] as const,
  lists: () => [...partyKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...partyKeys.lists(), { filters }] as const,
  details: () => [...partyKeys.all, 'detail'] as const,
  detail: (id: string) => [...partyKeys.details(), id] as const,
};

export function useParties(filters: Record<string, any> = {}) {
  return useQuery({
    queryKey: partyKeys.list(filters),
    queryFn: () => partyApi.getParties(filters),
  });
}

export function useParty(id: string) {
  return useQuery({
    queryKey: partyKeys.detail(id),
    queryFn: () => partyApi.getParty(id),
    enabled: !!id,
  });
}

export function useCreateParty() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PartyCreateDto) => partyApi.createParty(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: partyKeys.all });
    },
  });
}

export function useUpdateParty(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PartyUpdateDto) => partyApi.updateParty(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: partyKeys.all });
      queryClient.invalidateQueries({ queryKey: partyKeys.detail(id) });
    },
  });
}

export function useUpdatePartyStatus(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (isActive: boolean) => partyApi.updatePartyStatus(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: partyKeys.all });
      queryClient.invalidateQueries({ queryKey: partyKeys.detail(id) });
    },
  });
}

export function useDeleteParty() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => partyApi.deleteParty(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: partyKeys.all });
    },
  });
}
