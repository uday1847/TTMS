import type { ReactNode } from 'react'

interface FormFieldProps {
  label: string
  error?: string
  children: ReactNode
  required?: boolean
}

export function FormField({ label, error, children, required }: FormFieldProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        {label}
        {required && <span className="text-destructive ml-1">*</span>}
      </label>
      {children}
      {error && <p className="text-[0.8rem] font-medium text-destructive">{error}</p>}
    </div>
  )
}
