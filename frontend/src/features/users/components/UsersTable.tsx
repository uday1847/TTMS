import { useMemo } from 'react'
import type { ColumnDef } from '@tanstack/react-table'
import { DataTable, DataTableColumnHeader } from '@/shared/components/data-table'
import { PermissionGuard } from '@/shared/auth'
import { UserStatusSwitch } from './UserStatusSwitch'
import { Edit2, Trash2, Shield } from 'lucide-react'
import type { UserResponse } from '../api'

interface UsersTableProps {
  data: UserResponse[]
  isLoading: boolean
  onEdit: (user: UserResponse) => void
  onDelete: (user: UserResponse) => void
  onManageAccess: (user: UserResponse) => void
}

export function UsersTable({ data, isLoading, onEdit, onDelete, onManageAccess }: UsersTableProps) {
  const columns = useMemo<ColumnDef<UserResponse>[]>(
    () => [
      {
        accessorKey: 'username',
        header: ({ column }) => <DataTableColumnHeader column={column} title="Username" />,
        cell: ({ row }) => <div className="font-medium">{row.getValue('username')}</div>,
      },
      {
        accessorKey: 'email',
        header: ({ column }) => <DataTableColumnHeader column={column} title="Email" />,
      },
      {
        accessorKey: 'firstName',
        header: ({ column }) => <DataTableColumnHeader column={column} title="First Name" />,
      },
      {
        accessorKey: 'lastName',
        header: ({ column }) => <DataTableColumnHeader column={column} title="Last Name" />,
      },
      {
        id: 'roles',
        header: 'Roles',
        cell: ({ row }) => {
          const roles = row.original.roles
          if (!roles || roles.length === 0) return <span className="text-muted-foreground text-xs">No roles</span>
          return (
            <div className="flex gap-1 flex-wrap">
              {roles.map(r => (
                <span key={r.id} className="bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full font-medium">
                  {r.name}
                </span>
              ))}
            </div>
          )
        }
      },
      {
        accessorKey: 'isActive',
        header: 'Status',
        cell: ({ row }) => {
          return (
            <PermissionGuard permission="users:update" fallback={
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${row.original.isActive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                {row.original.isActive ? 'Active' : 'Inactive'}
              </span>
            }>
              <UserStatusSwitch userId={row.original.id} isActive={row.original.isActive} />
            </PermissionGuard>
          )
        },
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => {
          const user = row.original
          return (
            <div className="flex items-center space-x-2">
              <PermissionGuard permission="users:role_assign">
                <button
                  title="Manage Access"
                  className="p-2 hover:bg-muted rounded-md transition-colors text-muted-foreground hover:text-primary"
                  onClick={() => onManageAccess(user)}
                >
                  <Shield className="h-4 w-4" />
                </button>
              </PermissionGuard>
              
              <PermissionGuard permission="users:update">
                <button
                  title="Edit User"
                  className="p-2 hover:bg-muted rounded-md transition-colors text-muted-foreground hover:text-foreground"
                  onClick={() => onEdit(user)}
                >
                  <Edit2 className="h-4 w-4" />
                </button>
              </PermissionGuard>
              
              <PermissionGuard permission="users:delete">
                <button
                  title="Delete User"
                  className="p-2 hover:bg-destructive/10 rounded-md transition-colors text-muted-foreground hover:text-destructive"
                  onClick={() => onDelete(user)}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </PermissionGuard>
            </div>
          )
        },
      },
    ],
    [onEdit, onDelete, onManageAccess]
  )

  return <DataTable columns={columns} data={data} isLoading={isLoading} emptyMessage="No users found." />
}
