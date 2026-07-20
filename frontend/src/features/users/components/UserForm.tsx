import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { FormField, FormInput, FormActions } from '@/shared/components/form'
import { userSchema, type UserFormValues } from '../schemas/user.schema'
import type { UserResponseDto } from '../types/user.types'

interface UserFormProps {
  initialData?: UserResponseDto
  onSubmit: (data: UserFormValues) => void
  isLoading?: boolean
  onCancel?: () => void
}

export function UserForm({ initialData, onSubmit, isLoading, onCancel }: UserFormProps) {
  const isEditing = !!initialData

  const form = useForm<UserFormValues>({
    resolver: zodResolver(userSchema),
    defaultValues: initialData
      ? {
          email: initialData.email,
          username: initialData.username,
          firstName: initialData.firstName,
          lastName: initialData.lastName,
          phone: initialData.phone || '',
          isActive: initialData.isActive,
          roleIds: initialData.roles?.map(r => r.id) || [],
        }
      : {
          email: '',
          username: '',
          password: '',
          firstName: '',
          lastName: '',
          phone: '',
          isActive: true,
          roleIds: [],
        },
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Email" required error={form.formState.errors.email?.message}>
          <FormInput
            type="email"
            placeholder="john@example.com"
            {...form.register('email')}
            error={!!form.formState.errors.email}
          />
        </FormField>

        <FormField label="Username" required error={form.formState.errors.username?.message}>
          <FormInput
            placeholder="johndoe"
            {...form.register('username')}
            error={!!form.formState.errors.username}
          />
        </FormField>

        <FormField label="First Name" required error={form.formState.errors.firstName?.message}>
          <FormInput
            placeholder="John"
            {...form.register('firstName')}
            error={!!form.formState.errors.firstName}
          />
        </FormField>

        <FormField label="Last Name" required error={form.formState.errors.lastName?.message}>
          <FormInput
            placeholder="Doe"
            {...form.register('lastName')}
            error={!!form.formState.errors.lastName}
          />
        </FormField>

        {!isEditing && (
          <FormField label="Password" required error={form.formState.errors.password?.message}>
            <FormInput
              type="password"
              placeholder="••••••••"
              {...form.register('password')}
              error={!!form.formState.errors.password}
            />
          </FormField>
        )}

        <FormField label="Phone (Optional)" error={form.formState.errors.phone?.message}>
          <FormInput
            type="tel"
            placeholder="+1234567890"
            {...form.register('phone')}
            error={!!form.formState.errors.phone}
          />
        </FormField>
      </div>

      <div className="flex items-center mt-4">
        <input
          type="checkbox"
          {...form.register('isActive')}
          id="isActive"
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="isActive" className="ml-2 block text-sm text-gray-900">
          Account Active
        </label>
      </div>

      <FormActions>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium rounded-md border border-input hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring"
            disabled={isLoading}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 flex items-center"
          disabled={isLoading}
        >
          {isLoading && (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isEditing ? 'Save Changes' : 'Create User'}
        </button>
      </FormActions>
    </form>
  )
}
