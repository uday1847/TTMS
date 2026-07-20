import { useDeleteDriver } from '../hooks/use-drivers'

interface DeleteDriverDialogProps {
  isOpen: boolean
  driverId: string
  driverName: string
  onClose: () => void
}

export function DeleteDriverDialog({ isOpen, driverId, driverName, onClose }: DeleteDriverDialogProps) {
  const { mutate: deleteDriver, isPending } = useDeleteDriver()

  if (!isOpen) return null

  const handleDelete = () => {
    deleteDriver(driverId, {
      onSuccess: () => {
        onClose()
      },
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 animate-in zoom-in-95 duration-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Delete Driver</h2>
        <p className="text-sm text-gray-500 mb-6">
          Are you sure you want to delete the driver <strong>{driverName}</strong>? This action will soft-delete the driver profile. Active trips may prevent this action.
        </p>
        <div className="flex justify-end space-x-2">
          <button
            onClick={onClose}
            disabled={isPending}
            className="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 focus:outline-none"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={isPending}
            className="px-4 py-2 text-sm font-medium rounded-md bg-red-600 text-white hover:bg-red-700 focus:outline-none flex items-center"
          >
            {isPending && (
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
