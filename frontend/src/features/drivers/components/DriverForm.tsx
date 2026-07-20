import { useForm, type SubmitHandler } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { FormField, FormInput, FormActions } from '@/shared/components/form'
import { driverSchema, type DriverFormValues } from '../schemas/driver.schema'
import type { DriverResponseDto } from '../types/driver.types'

interface DriverFormProps {
  initialData?: DriverResponseDto
  onSubmit: SubmitHandler<DriverFormValues>
  isLoading?: boolean
  onCancel?: () => void
}

export function DriverForm({ initialData, onSubmit, isLoading, onCancel }: DriverFormProps) {
  const isEditing = !!initialData

  const form = useForm<DriverFormValues>({
    resolver: zodResolver(driverSchema) as any,
    defaultValues: initialData
      ? {
          name: initialData.name,
          address: initialData.address || '',
          employeeCode: initialData.employeeCode,
          licenseNumber: initialData.licenseNumber,
          licenseExpiry: initialData.licenseExpiry,
          licenseClass: initialData.licenseClass,
          contactPhone: initialData.contactPhone,
          emergencyContactPhone: initialData.emergencyContactPhone || '',
          fixedSalary: initialData.fixedSalary,
          commissionPercentage: initialData.commissionPercentage,
          driverType: initialData.driverType,
          currentStatus: initialData.currentStatus,
        }
      : {
          name: '',
          address: '',
          employeeCode: '',
          licenseNumber: '',
          licenseExpiry: '',
          licenseClass: '',
          contactPhone: '',
          emergencyContactPhone: '',
          fixedSalary: 0,
          commissionPercentage: 0,
          driverType: '',
          currentStatus: 'available',
        },
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit as any)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Full Name" required error={form.formState.errors.name?.message}>
          <FormInput placeholder="Raj Kumar" {...form.register('name')} error={!!form.formState.errors.name} />
        </FormField>

        <FormField label="Employee Code" required error={form.formState.errors.employeeCode?.message}>
          <FormInput placeholder="DRV-101" {...form.register('employeeCode')} error={!!form.formState.errors.employeeCode} />
        </FormField>

        <FormField label="License Number" required error={form.formState.errors.licenseNumber?.message}>
          <FormInput placeholder="DL-12345" {...form.register('licenseNumber')} error={!!form.formState.errors.licenseNumber} />
        </FormField>

        <FormField label="License Expiry" required error={form.formState.errors.licenseExpiry?.message}>
          <FormInput type="date" {...form.register('licenseExpiry')} error={!!form.formState.errors.licenseExpiry} />
        </FormField>

        <FormField label="License Class" required error={form.formState.errors.licenseClass?.message}>
          <FormInput placeholder="Heavy Duty" {...form.register('licenseClass')} error={!!form.formState.errors.licenseClass} />
        </FormField>

        <FormField label="Driver Type" required error={form.formState.errors.driverType?.message}>
          <select
            {...form.register('driverType')}
            className={`flex h-10 w-full rounded-md border ${
              form.formState.errors.driverType ? 'border-red-500' : 'border-input'
            } bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
          >
            <option value="">Select Type</option>
            <option value="SALARIED">SALARIED</option>
            <option value="COMMISSION_BASED">COMMISSION BASED</option>
            <option value="CONTRACT">CONTRACT</option>
          </select>
        </FormField>

        <FormField label="Contact Phone" required error={form.formState.errors.contactPhone?.message}>
          <FormInput placeholder="+919999988888" {...form.register('contactPhone')} error={!!form.formState.errors.contactPhone} />
        </FormField>

        <FormField label="Emergency Contact Phone" error={form.formState.errors.emergencyContactPhone?.message}>
          <FormInput placeholder="+919999911111" {...form.register('emergencyContactPhone')} error={!!form.formState.errors.emergencyContactPhone} />
        </FormField>

        <FormField label="Fixed Salary" error={form.formState.errors.fixedSalary?.message}>
          <FormInput type="number" step="0.01" {...form.register('fixedSalary')} error={!!form.formState.errors.fixedSalary} />
        </FormField>

        <FormField label="Commission Percentage" error={form.formState.errors.commissionPercentage?.message}>
          <FormInput type="number" step="0.1" {...form.register('commissionPercentage')} error={!!form.formState.errors.commissionPercentage} />
        </FormField>

        <FormField label="Address" error={form.formState.errors.address?.message}>
          <FormInput placeholder="123 Quarry Road" {...form.register('address')} error={!!form.formState.errors.address} />
        </FormField>

        <FormField label="Status" error={form.formState.errors.currentStatus?.message}>
          <select
            {...form.register('currentStatus')}
            className={`flex h-10 w-full rounded-md border ${
              form.formState.errors.currentStatus ? 'border-red-500' : 'border-input'
            } bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
          >
            <option value="available">Available</option>
            <option value="on_trip">On Trip</option>
            <option value="on_leave">On Leave</option>
            <option value="inactive">Inactive</option>
          </select>
        </FormField>
      </div>

      <FormActions>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 hover:bg-gray-50 focus:outline-none"
            disabled={isLoading}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium rounded-md bg-blue-600 text-white hover:bg-blue-700 focus:outline-none disabled:opacity-50 flex items-center"
          disabled={isLoading}
        >
          {isLoading && (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isEditing ? 'Save Changes' : 'Create Driver'}
        </button>
      </FormActions>
    </form>
  )
}
