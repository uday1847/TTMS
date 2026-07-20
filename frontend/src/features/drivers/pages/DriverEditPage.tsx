import { useParams, useNavigate } from 'react-router'
import { DriverForm } from '../components/DriverForm'
import { useDriver, useUpdateDriver } from '../hooks/use-drivers'
import type { DriverFormValues } from '../schemas/driver.schema'
import type { DriverUpdateDto } from '../types/driver.types'

export default function DriverEditPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const { data: driver, isLoading: isFetching } = useDriver(id!)
  const { mutate: updateDriver, isPending: isUpdating } = useUpdateDriver()

  const handleSubmit = (data: DriverFormValues) => {
    updateDriver({ id: id!, data: data as DriverUpdateDto }, {
      onSuccess: () => {
        navigate('/drivers')
      }
    })
  }

  if (isFetching) {
    return (
      <div className="p-6 max-w-4xl mx-auto flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!driver) {
    return (
      <div className="p-6 max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[50vh] text-center">
        <h2 className="text-xl font-bold text-gray-900">Driver Not Found</h2>
        <p className="text-gray-500 mt-2">The driver you are looking for does not exist or has been deleted.</p>
        <button onClick={() => navigate('/drivers')} className="mt-4 text-blue-600 hover:underline">
          Return to Drivers List
        </button>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Edit Driver</h1>
        <p className="text-sm text-gray-500">Update configuration values for {driver.name}.</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <DriverForm
          initialData={driver}
          onSubmit={handleSubmit}
          isLoading={isUpdating}
          onCancel={() => navigate('/drivers')}
        />
      </div>
    </div>
  )
}
