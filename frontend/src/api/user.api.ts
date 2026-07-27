import { api } from '@/lib/axios';
import type { APIResponse } from '@/shared/types/api.types';
import type {
  PaginatedUsersDto,
  UserResponseDto,
  UserCreateDto,
  UserUpdateDto,
  UserRoleUpdateDto,
  UserPermissionOverrideUpdateDto,
} from '../features/users/types/user.types';

export async function getUsers(params: {
  page?: number;
  size?: number;
  q?: string;
}): Promise<PaginatedUsersDto> {
  const response = await api.get<APIResponse<PaginatedUsersDto>>('/users', {
    params,
  });
  return response.data.data;
}

export async function getUser(id: string): Promise<UserResponseDto> {
  const response = await api.get<APIResponse<UserResponseDto>>(`/users/${id}`);
  return response.data.data;
}

export async function createUser(data: UserCreateDto): Promise<UserResponseDto> {
  const response = await api.post<APIResponse<UserResponseDto>>('/users', data);
  return response.data.data;
}

export async function updateUser(id: string, data: UserUpdateDto): Promise<UserResponseDto> {
  const response = await api.put<APIResponse<UserResponseDto>>(`/users/${id}`, data);
  return response.data.data;
}

export async function patchUser(id: string, data: Partial<UserUpdateDto>): Promise<UserResponseDto> {
  const response = await api.patch<APIResponse<UserResponseDto>>(`/users/${id}`, data);
  return response.data.data;
}

export async function deleteUser(id: string): Promise<void> {
  await api.delete<APIResponse<null>>(`/users/${id}`);
}

export async function assignUserRole(id: string, roleName: string): Promise<UserResponseDto> {
  const response = await api.post<APIResponse<UserResponseDto>>(`/users/${id}/roles/${roleName}`);
  return response.data.data;
}

export async function removeUserRole(id: string, roleName: string): Promise<UserResponseDto> {
  const response = await api.delete<APIResponse<UserResponseDto>>(`/users/${id}/roles/${roleName}`);
  return response.data.data;
}

export async function getUserAccessProfile(id: string): Promise<UserResponseDto> {
  const response = await api.get<APIResponse<UserResponseDto>>(`/users/${id}/access-profile`);
  return response.data.data;
}

export async function updateUserRoles(id: string, data: UserRoleUpdateDto): Promise<UserResponseDto> {
  const response = await api.put<APIResponse<UserResponseDto>>(`/users/${id}/roles`, data);
  return response.data.data;
}

export async function updateUserPermissionOverrides(
  id: string,
  data: UserPermissionOverrideUpdateDto
): Promise<UserResponseDto> {
  const response = await api.put<APIResponse<UserResponseDto>>(`/users/${id}/permissions`, data);
  return response.data.data;
}

export async function getEffectivePermissions(id: string): Promise<string[]> {
  const response = await api.get<APIResponse<string[]>>(`/users/${id}/effective-permissions`);
  return response.data.data;
}
