import { useQuery } from '@tanstack/react-query';
import { getUser, getUserAccessProfile } from '../../../api/user.api';

export const useUser = (id: string, includeAccessProfile = false) => {
  return useQuery({
    queryKey: ['users', id, { includeAccessProfile }],
    queryFn: () => (includeAccessProfile ? getUserAccessProfile(id) : getUser(id)),
    enabled: !!id,
  });
};
