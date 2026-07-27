import { useDeleteUser } from '../hooks/use-delete-user'
import { Loader2 } from 'lucide-react'
import { showApiError } from '@/shared/error'

interface UserDeleteDialogProps {
  userId: string
  userName: string
  isOpen: boolean
  onClose: () => void
}

export function UserDeleteDialog({ userId, userName, isOpen, onClose }: UserDeleteDialogProps) {
  const { mutate, isPending } = useDeleteUser()

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="bg-card border border-border shadow-lg rounded-lg w-full max-w-md p-6 animate-in fade-in zoom-in duration-200">
        <h2 className="text-lg font-semibold mb-2">Delete User</h2>
        <p className="text-sm text-muted-foreground mb-6">
          Are you sure you want to delete the user <strong>{userName}</strong>? This action cannot be undone.
        </p>
        
        <div className="flex justify-end space-x-2">
          <button
            className="px-4 py-2 text-sm font-medium rounded-md border border-input hover:bg-accent focus:outline-none"
            onClick={onClose}
            disabled={isPending}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 text-sm font-medium rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90 focus:outline-none flex items-center disabled:opacity-50"
            disabled={isPending}
            onClick={() => {
              mutate(userId, {
                onSuccess: () => {
                  onClose()
                },
                onError: (error) => {
                  showApiError(error, 'Delete Failed')
                }
              })
            }}
          >
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
