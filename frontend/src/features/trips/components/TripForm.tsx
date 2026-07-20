import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { tripSchema, type TripFormData } from '../schemas/trip.schema';
import type { TripResponseDto } from '../types/trip.types';
import { FormField, FormInput, FormActions } from '@/shared/components/form';
// Mock hook until Party module is fully implemented in frontend
const useParties = (_options?: any) => ({
  data: { items: [] as { id: string, name: string }[], total: 0, page: 1, size: 10 },
  isLoading: false
});
import { useTractors } from '@/features/tractors/hooks/use-tractors';
import { useDrivers } from '@/features/drivers/hooks/use-drivers';
import { Loader2 } from 'lucide-react';
import dayjs from 'dayjs';

interface TripFormProps {
  initialData?: TripResponseDto;
  onSubmit: (data: TripFormData) => Promise<void>;
  isLoading: boolean;
  onCancel?: () => void;
}

export function TripForm({ initialData, onSubmit, isLoading, onCancel }: TripFormProps) {
  const isEditing = !!initialData;
  const isLocked = isEditing && initialData.status !== 'PENDING' && initialData.status !== 'CANCELLED';

  const { data: partiesResponse, isLoading: isLoadingParties } = useParties({ size: 1000 });
  const { data: tractorsResponse, isLoading: isLoadingTractors } = useTractors({ size: 1000, status: 'AVAILABLE' });
  const { data: driversResponse, isLoading: isLoadingDrivers } = useDrivers({ size: 1000, status: 'AVAILABLE' });

  const form = useForm<TripFormData>({
    resolver: zodResolver(tripSchema) as any,
    defaultValues: initialData
      ? {
          party_id: initialData.party_id,
          tractor_id: initialData.tractor_id,
          driver_id: initialData.driver_id,
          source_location: initialData.source_location,
          destination_location: initialData.destination_location,
          trip_date: dayjs(initialData.trip_date).format('YYYY-MM-DD'),
          expected_delivery_date: dayjs(initialData.expected_delivery_date).format('YYYY-MM-DD'),
          freight_amount: initialData.freight_amount,
          advance_amount: initialData.advance_amount,
          remarks: initialData.remarks || '',
        }
      : {
          trip_date: dayjs().format('YYYY-MM-DD'),
          freight_amount: 0,
          advance_amount: 0,
        },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit as any)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormField label="Party / Customer" required error={form.formState.errors.party_id?.message}>
          <select
            {...form.register('party_id')}
            disabled={isLocked || isLoadingParties}
            className={`flex h-10 w-full rounded-md border ${
              form.formState.errors.party_id ? 'border-red-500' : 'border-input'
            } bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
          >
            <option value="">Select Party</option>
            {partiesResponse?.items.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
            {initialData?.party_id && !partiesResponse?.items.some(p => p.id === initialData.party_id) && (
              <option value={initialData.party_id}>Current Party</option>
            )}
          </select>
        </FormField>

        <FormField label="Assigned Tractor" required error={form.formState.errors.tractor_id?.message}>
          <select
            {...form.register('tractor_id')}
            disabled={isLocked || isLoadingTractors}
            className={`flex h-10 w-full rounded-md border ${
              form.formState.errors.tractor_id ? 'border-red-500' : 'border-input'
            } bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
          >
            <option value="">Select Tractor</option>
            {tractorsResponse?.items.map(t => (
              <option key={t.id} value={t.id}>{t.tractor_number}</option>
            ))}
            {initialData?.tractor_id && !tractorsResponse?.items.some(t => t.id === initialData.tractor_id) && (
              <option value={initialData.tractor_id}>Current Tractor</option>
            )}
          </select>
        </FormField>

        <FormField label="Assigned Driver" required error={form.formState.errors.driver_id?.message}>
          <select
            {...form.register('driver_id')}
            disabled={isLocked || isLoadingDrivers}
            className={`flex h-10 w-full rounded-md border ${
              form.formState.errors.driver_id ? 'border-red-500' : 'border-input'
            } bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
          >
            <option value="">Select Driver</option>
            {driversResponse?.items.map(d => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
            {initialData?.driver_id && !driversResponse?.items.some(d => d.id === initialData.driver_id) && (
              <option value={initialData.driver_id}>Current Driver</option>
            )}
          </select>
        </FormField>

        <FormField label="Source Location" required error={form.formState.errors.source_location?.message}>
          <FormInput placeholder="Origin City" {...form.register('source_location')} error={!!form.formState.errors.source_location} />
        </FormField>

        <FormField label="Destination Location" required error={form.formState.errors.destination_location?.message}>
          <FormInput placeholder="Destination City" {...form.register('destination_location')} error={!!form.formState.errors.destination_location} />
        </FormField>

        <FormField label="Trip Date" required error={form.formState.errors.trip_date?.message}>
          <FormInput type="date" {...form.register('trip_date')} error={!!form.formState.errors.trip_date} />
        </FormField>

        <FormField label="Expected Delivery Date" required error={form.formState.errors.expected_delivery_date?.message}>
          <FormInput type="date" {...form.register('expected_delivery_date')} error={!!form.formState.errors.expected_delivery_date} />
        </FormField>

        <FormField label="Freight Amount" required error={form.formState.errors.freight_amount?.message}>
          <FormInput type="number" step="0.01" disabled={isLocked} {...form.register('freight_amount', { valueAsNumber: true })} error={!!form.formState.errors.freight_amount} />
        </FormField>

        <FormField label="Advance Amount" required error={form.formState.errors.advance_amount?.message}>
          <FormInput type="number" step="0.01" {...form.register('advance_amount', { valueAsNumber: true })} error={!!form.formState.errors.advance_amount} />
        </FormField>

        <div className="md:col-span-2">
          <FormField label="Remarks" error={form.formState.errors.remarks?.message}>
            <textarea
              className={`flex min-h-[80px] w-full rounded-md border ${
                form.formState.errors.remarks ? 'border-red-500' : 'border-input'
              } bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
              placeholder="Any additional notes..."
              {...form.register('remarks')}
            />
          </FormField>
        </div>
      </div>

      <FormActions>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground focus:outline-none"
            disabled={isLoading}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 focus:outline-none disabled:opacity-50 flex items-center"
          disabled={isLoading}
        >
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isEditing ? 'Update Trip' : 'Create Trip'}
        </button>
      </FormActions>
    </form>
  );
}
