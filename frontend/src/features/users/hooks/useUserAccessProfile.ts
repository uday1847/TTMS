import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api'

export function useUserAccessProfile(userId: string | undefined) {
  return useQuery({
    queryKey: ['users', userId, 'access-profile'],
    queryFn: () => usersApi.getAccessProfile(userId!),
    enabled: !!userId,
  })
}

export function useUpdateUserRoles() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, roleIds }: { id: string; roleIds: string[] }) =>
      usersApi.updateRoles(id, { roleIds }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['users'] }) // list
    },
  })
}

export function useUpdateUserPermissions() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, grantPermissions, revokePermissions }: { id: string; grantPermissions: string[]; revokePermissions: string[] }) =>
      usersApi.updatePermissionOverrides(id, { grantPermissions, revokePermissions }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users', variables.id] })
    },
  })
}
