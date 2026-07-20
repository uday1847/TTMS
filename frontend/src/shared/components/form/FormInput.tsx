import { forwardRef, type InputHTMLAttributes } from 'react'

export interface FormInputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
}

export const FormInput = forwardRef<HTMLInputElement, FormInputProps>(
  ({ className = '', error, ...props }, ref) => {
    return (
      <input
        className={`flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 ${
          error ? 'border-destructive focus-visible:ring-destructive' : 'border-input'
        } ${className}`}
        ref={ref}
        {...props}
      />
    )
  }
)
FormInput.displayName = 'FormInput'
