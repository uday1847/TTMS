import { useQuery } from '@tanstack/react-query';
import { getUsers } from '../../../api/user.api';

export const useUsers = (page?: number, size?: number, q?: string) => {
  return useQuery({
    queryKey: ['users', { page, size, q }],
    queryFn: () => getUsers({ page, size, q }),
  });
};
