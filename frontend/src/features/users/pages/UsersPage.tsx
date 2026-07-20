import { useState } from 'react'
import { useUsers, useCreateUser, useUpdateUser } from '../hooks'
import { UsersTable, UserForm, UserDeleteDialog, UserAccessProfileDrawer } from '../components'
import { Pagination, SearchInput } from '@/shared/components/data-table'
import { PermissionGuard } from '@/shared/auth'
import { Plus } from 'lucide-react'
import type { UserResponse, UserCreate, UserUpdate } from '../api'

export default function UsersPage() {
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(10)
  const [q, setQ] = useState('')

  const { data, isLoading } = useUsers({ page, size, q })
  const { mutateAsync: createUser, isPending: isCreating } = useCreateUser()
  const { mutateAsync: updateUser, isPending: isUpdating } = useUpdateUser()

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<UserResponse | undefined>()
  const [deletingUser, setDeletingUser] = useState<UserResponse | undefined>()
  const [accessProfileUserId, setAccessProfileUserId] = useState<string | undefined>()

  const handleOpenCreate = () => {
    setEditingUser(undefined)
    setIsFormOpen(true)
  }

  const handleOpenEdit = (user: UserResponse) => {
    setEditingUser(user)
    setIsFormOpen(true)
  }

  const handleFormSubmit = async (formData: any) => {
    try {
      if (editingUser) {
        await updateUser({ id: editingUser.id, data: formData as UserUpdate })
      } else {
        const { isActive, ...createData } = formData
        await createUser(createData as UserCreate)
      }
      setIsFormOpen(false)
    } catch (error) {
      // Error handled by hook's onError Toaster
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="text-sm text-muted-foreground">Manage system users and their access.</p>
        </div>
        <PermissionGuard permission="users:create">
          <button
            onClick={handleOpenCreate}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium h-10 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <Plus className="mr-2 h-4 w-4" /> Add User
          </button>
        </PermissionGuard>
      </div>

      <div className="flex items-center justify-between">
        <SearchInput
          value={q}
          onChange={(val) => {
            setQ(val)
            setPage(1)
          }}
          placeholder="Search by name or email..."
        />
      </div>

      <UsersTable
        data={data?.items || []}
        isLoading={isLoading}
        onEdit={handleOpenEdit}
        onDelete={setDeletingUser}
        onManageAccess={(user) => setAccessProfileUserId(user.id)}
      />

      {!!data && data.total > 0 && (
        <Pagination
          page={page}
          size={size}
          total={data.total}
          onPageChange={setPage}
          onSizeChange={(newSize) => {
            setSize(newSize)
            setPage(1)
          }}
        />
      )}

      {/* Form Modal */}
      {isFormOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-card border border-border shadow-lg rounded-lg w-full max-w-2xl p-6 animate-in fade-in zoom-in duration-200 my-8">
            <h2 className="text-lg font-semibold mb-6">
              {editingUser ? 'Edit User' : 'Create User'}
            </h2>
            <UserForm
              initialData={editingUser}
              onSubmit={handleFormSubmit}
              isLoading={isCreating || isUpdating}
              onCancel={() => setIsFormOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      <UserDeleteDialog
        isOpen={!!deletingUser}
        userId={deletingUser?.id || ''}
        userName={deletingUser?.email || ''}
        onClose={() => setDeletingUser(undefined)}
      />

      {/* Access Profile Drawer */}
      <UserAccessProfileDrawer
        userId={accessProfileUserId}
        isOpen={!!accessProfileUserId}
        onClose={() => setAccessProfileUserId(undefined)}
      />
    </div>
  )
}
