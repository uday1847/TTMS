import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { FormField, FormInput, FormActions } from '@/shared/components/form';
import { tractorSchema, type TractorFormValues } from '../schemas/tractor.schema';
import type { TractorResponseDto } from '../types/tractor.types';

interface TractorFormProps {
  initialData?: TractorResponseDto;
  onSubmit: SubmitHandler<TractorFormValues>;
  isLoading?: boolean;
  onCancel?: () => void;
}

export function TractorForm({ initialData, onSubmit, isLoading, onCancel }: TractorFormProps) {
  const isEditing = !!initialData;

  const form = useForm<TractorFormValues>({
    resolver: zodResolver(tractorSchema) as any,
    defaultValues: initialData
      ? {
          tractor_number: initialData.tractor_number,
          owner_name: initialData.owner_name,
          rc_number: initialData.rc_number,
          insurance_number: initialData.insurance_number || '',
          insurance_expiry: initialData.insurance_expiry,
          manufacturer: initialData.manufacturer || '',
          model: initialData.model || '',
          registration_date: initialData.registration_date || '',
          remarks: initialData.remarks || '',
          fuel_capacity: initialData.fuel_capacity ?? undefined,
        }
      : {
          tractor_number: '',
          owner_name: '',
          rc_number: '',
          insurance_number: '',
          insurance_expiry: '',
          manufacturer: '',
          model: '',
          registration_date: '',
          remarks: '',
          fuel_capacity: undefined,
        },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit as any)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Tractor Number" required error={form.formState.errors.tractor_number?.message}>
          <FormInput placeholder="RJ-14-1234" {...form.register('tractor_number')} error={!!form.formState.errors.tractor_number} />
        </FormField>

        <FormField label="Owner Name" required error={form.formState.errors.owner_name?.message}>
          <FormInput placeholder="Jaipur Logistics Ltd" {...form.register('owner_name')} error={!!form.formState.errors.owner_name} />
        </FormField>

        <FormField label="RC Number" required error={form.formState.errors.rc_number?.message}>
          <FormInput placeholder="RC-JAIPUR-888999" {...form.register('rc_number')} error={!!form.formState.errors.rc_number} />
        </FormField>

        <FormField label="Insurance Number" error={form.formState.errors.insurance_number?.message}>
          <FormInput placeholder="INS-TR-990011" {...form.register('insurance_number')} error={!!form.formState.errors.insurance_number} />
        </FormField>

        <FormField label="Insurance Expiry" required error={form.formState.errors.insurance_expiry?.message}>
          <FormInput type="date" {...form.register('insurance_expiry')} error={!!form.formState.errors.insurance_expiry} />
        </FormField>

        <FormField label="Manufacturer" error={form.formState.errors.manufacturer?.message}>
          <FormInput placeholder="Mahindra & Mahindra" {...form.register('manufacturer')} error={!!form.formState.errors.manufacturer} />
        </FormField>

        <FormField label="Model" error={form.formState.errors.model?.message}>
          <FormInput placeholder="Arjun 555 DI" {...form.register('model')} error={!!form.formState.errors.model} />
        </FormField>

        <FormField label="Registration Date" error={form.formState.errors.registration_date?.message}>
          <FormInput type="date" {...form.register('registration_date')} error={!!form.formState.errors.registration_date} />
        </FormField>

        <FormField label="Fuel Capacity (Liters)" error={form.formState.errors.fuel_capacity?.message}>
          <FormInput type="number" {...form.register('fuel_capacity')} error={!!form.formState.errors.fuel_capacity} />
        </FormField>

        <div className="md:col-span-2">
          <FormField label="Remarks" error={form.formState.errors.remarks?.message}>
            <FormInput placeholder="Any additional notes" {...form.register('remarks')} error={!!form.formState.errors.remarks} />
          </FormField>
        </div>
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
          {isEditing ? 'Save Changes' : 'Create Tractor'}
        </button>
      </FormActions>
    </form>
  );
}
