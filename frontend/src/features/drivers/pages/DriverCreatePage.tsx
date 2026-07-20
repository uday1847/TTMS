import { useNavigate } from 'react-router'
import { DriverForm } from '../components/DriverForm'
import { useCreateDriver } from '../hooks/use-drivers'
import type { DriverFormValues } from '../schemas/driver.schema'
import type { DriverCreateDto } from '../types/driver.types'

export default function DriverCreatePage() {
  const navigate = useNavigate()
  const { mutate: createDriver, isPending } = useCreateDriver()

  const handleSubmit = (data: DriverFormValues) => {
    createDriver(data as DriverCreateDto, {
      onSuccess: () => {
        navigate('/drivers')
      }
    })
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Add Driver</h1>
        <p className="text-sm text-gray-500">Register a new driver profile in the system.</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <DriverForm
          onSubmit={handleSubmit}
          isLoading={isPending}
          onCancel={() => navigate('/drivers')}
        />
      </div>
    </div>
  )
}
