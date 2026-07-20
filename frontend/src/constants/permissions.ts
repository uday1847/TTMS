export const PERMISSIONS = {
  // Users
  USERS_READ: 'users:read',
  USERS_CREATE: 'users:create',
  USERS_UPDATE: 'users:update',
  USERS_DELETE: 'users:delete',
  USERS_ROLE_ASSIGN: 'users:role_assign',

  // Roles
  ROLES_READ: 'roles:read',
  ROLES_CREATE: 'roles:create',
  ROLES_UPDATE: 'roles:update',
  ROLES_DELETE: 'roles:delete',
  ROLES_PERMISSION_ASSIGN: 'roles:permission_assign',

  // Permissions
  PERMISSIONS_READ: 'permissions:read',

  // Drivers
  DRIVERS_READ: 'drivers:read',
  DRIVERS_CREATE: 'drivers:create',
  DRIVERS_UPDATE: 'drivers:update',
  DRIVERS_DELETE: 'drivers:delete',

  // Tractors
  TRACTORS_READ: 'tractors:read',
  TRACTORS_CREATE: 'tractors:create',
  TRACTORS_UPDATE: 'tractors:update',
  TRACTORS_DELETE: 'tractors:delete',

  // Trips
  TRIPS_READ: 'trips:read',
  TRIPS_CREATE: 'trips:create',
  TRIPS_UPDATE: 'trips:update',
  TRIPS_DELETE: 'trips:delete',
} as const;

export type PermissionType = typeof PERMISSIONS[keyof typeof PERMISSIONS];
