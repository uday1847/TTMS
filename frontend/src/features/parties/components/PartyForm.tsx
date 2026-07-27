import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { partySchema, type PartyFormData } from '../schemas/party.schema';
import type { PartyResponseDto } from '../types/party.types';
import { PartyType } from '../types/party.types';
import { FormField, FormInput, FormActions } from '@/shared/components/form';
import { Loader2 } from 'lucide-react';

interface PartyFormProps {
  initialData?: PartyResponseDto;
  onSubmit: (data: PartyFormData) => Promise<void>;
  isLoading: boolean;
  onCancel?: () => void;
}

export function PartyForm({ initialData, onSubmit, isLoading, onCancel }: PartyFormProps) {
  const isEditing = !!initialData;

  const form = useForm<PartyFormData>({
    resolver: zodResolver(partySchema),
    defaultValues: initialData
      ? {
          name: initialData.name,
          party_type: initialData.party_type,
          mobile_number: initialData.mobile_number,
          alternate_mobile: initialData.alternate_mobile || '',
          email: initialData.email || '',
          gst_number: initialData.gst_number || '',
          pan_number: initialData.pan_number || '',
          address: initialData.address || '',
          city: initialData.city || '',
          state: initialData.state || '',
          pincode: initialData.pincode || '',
          contact_person: initialData.contact_person || '',
          opening_balance: initialData.opening_balance,
          credit_limit: initialData.credit_limit,
          remarks: initialData.remarks || '',
        }
      : {
          name: '',
          party_type: '' as any,
          mobile_number: '',
          alternate_mobile: '',
          email: '',
          gst_number: '',
          pan_number: '',
          address: '',
          city: '',
          state: '',
          pincode: '',
          contact_person: '',
          opening_balance: 0,
          credit_limit: 0,
          remarks: '',
        },
  });

  const handleFormSubmit = form.handleSubmit((data) => {
    // Transform GST and PAN to uppercase before submission
    const transformedData = {
      ...data,
      gst_number: data.gst_number?.toUpperCase(),
      pan_number: data.pan_number?.toUpperCase(),
    };
    return onSubmit(transformedData);
  });

  return (
    <form onSubmit={handleFormSubmit} className="space-y-8">
      {/* Basic Information */}
      <div>
        <h3 className="text-lg font-medium border-b pb-2 mb-4">Basic Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField label="Party Name" required error={form.formState.errors.name?.message}>
            <FormInput placeholder="Business or Person Name" {...form.register('name')} error={!!form.formState.errors.name} />
          </FormField>

          <FormField label="Party Type" required error={form.formState.errors.party_type?.message}>
            <select
              {...form.register('party_type')}
              className={`flex h-10 w-full rounded-md border ${
                form.formState.errors.party_type ? 'border-red-500' : 'border-input'
              } bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
            >
              <option value="" disabled>Select Type</option>
              <option value={PartyType.CUSTOMER}>Customer</option>
              <option value={PartyType.SUPPLIER}>Supplier</option>
              <option value={PartyType.BROKER}>Broker</option>
              <option value={PartyType.OTHER}>Other</option>
            </select>
          </FormField>

          <FormField label="Contact Person" error={form.formState.errors.contact_person?.message}>
            <FormInput placeholder="Key Account Person" {...form.register('contact_person')} error={!!form.formState.errors.contact_person} />
          </FormField>
        </div>
      </div>

      {/* Contact Information */}
      <div>
        <h3 className="text-lg font-medium border-b pb-2 mb-4">Contact Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FormField label="Mobile Number" required error={form.formState.errors.mobile_number?.message}>
            <FormInput placeholder="+91 XXXXX XXXXX" {...form.register('mobile_number')} error={!!form.formState.errors.mobile_number} />
          </FormField>

          <FormField label="Alternate Mobile" error={form.formState.errors.alternate_mobile?.message}>
            <FormInput placeholder="+91 XXXXX XXXXX" {...form.register('alternate_mobile')} error={!!form.formState.errors.alternate_mobile} />
          </FormField>

          <FormField label="Email" error={form.formState.errors.email?.message}>
            <FormInput placeholder="contact@example.com" {...form.register('email')} error={!!form.formState.errors.email} />
          </FormField>
        </div>
      </div>

      {/* Tax Information */}
      <div>
        <h3 className="text-lg font-medium border-b pb-2 mb-4">Tax Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField label="GST Number" error={form.formState.errors.gst_number?.message}>
            <FormInput placeholder="15-character GSTIN" className="uppercase" {...form.register('gst_number')} error={!!form.formState.errors.gst_number} />
          </FormField>

          <FormField label="PAN Number" error={form.formState.errors.pan_number?.message}>
            <FormInput placeholder="10-character PAN" className="uppercase" {...form.register('pan_number')} error={!!form.formState.errors.pan_number} />
          </FormField>
        </div>
      </div>

      {/* Location & Address */}
      <div>
        <h3 className="text-lg font-medium border-b pb-2 mb-4">Location & Address</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-3">
            <FormField label="Street Address" error={form.formState.errors.address?.message}>
              <textarea
                className={`flex min-h-[80px] w-full rounded-md border ${
                  form.formState.errors.address ? 'border-red-500' : 'border-input'
                } bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
                placeholder="Billing or physical address"
                {...form.register('address')}
              />
            </FormField>
          </div>

          <FormField label="City" error={form.formState.errors.city?.message}>
            <FormInput placeholder="City" {...form.register('city')} error={!!form.formState.errors.city} />
          </FormField>

          <FormField label="State" error={form.formState.errors.state?.message}>
            <FormInput placeholder="State" {...form.register('state')} error={!!form.formState.errors.state} />
          </FormField>

          <FormField label="Pincode" error={form.formState.errors.pincode?.message}>
            <FormInput placeholder="Postal/ZIP code" {...form.register('pincode')} error={!!form.formState.errors.pincode} />
          </FormField>
        </div>
      </div>

      {/* Financial Information */}
      <div>
        <h3 className="text-lg font-medium border-b pb-2 mb-4">Financial Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField label="Opening Balance" error={form.formState.errors.opening_balance?.message}>
            <FormInput type="number" step="0.01" {...form.register('opening_balance', { valueAsNumber: true })} error={!!form.formState.errors.opening_balance} />
          </FormField>

          <FormField label="Credit Limit" error={form.formState.errors.credit_limit?.message}>
            <FormInput type="number" step="0.01" {...form.register('credit_limit', { valueAsNumber: true })} error={!!form.formState.errors.credit_limit} />
          </FormField>
        </div>
      </div>

      {/* Additional */}
      <div>
        <h3 className="text-lg font-medium border-b pb-2 mb-4">Additional Notes</h3>
        <FormField label="Remarks" error={form.formState.errors.remarks?.message}>
          <textarea
            className={`flex min-h-[80px] w-full rounded-md border ${
              form.formState.errors.remarks ? 'border-red-500' : 'border-input'
            } bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
            placeholder="Any extra comments or audit notes"
            {...form.register('remarks')}
          />
        </FormField>
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
          {isEditing ? 'Update Party' : 'Create Party'}
        </button>
      </FormActions>
    </form>
  );
}
