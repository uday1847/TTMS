export interface UserResponseDto {
  id: string;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  phone?: string | null;
  status: 'ACTIVE' | 'INACTIVE' | 'LOCKED' | 'PENDING_VERIFICATION';
  isActive: boolean;
  createdAt: string;
  updatedAt?: string | null;
  roles: {
    id: string;
    name: string;
    displayName: string;
  }[];
  effectivePermissions: string[];
  directPermissions: string[];
}

export interface PaginatedUsersDto {
  items: UserResponseDto[];
  total: number;
  page: number;
  size: number;
}

export interface UserCreateDto {
  email: string;
  username: string;
  password?: string;
  firstName: string;
  lastName: string;
  phone?: string;
  roleIds?: string[];
}

export interface UserUpdateDto {
  firstName?: string;
  lastName?: string;
  email?: string;
  username?: string;
  phone?: string;
  isActive?: boolean;
  roleIds?: string[];
}

export interface UserRoleUpdateDto {
  roleIds: string[];
}

export interface UserPermissionOverrideUpdateDto {
  grantPermissions: string[];
  revokePermissions: string[];
}
