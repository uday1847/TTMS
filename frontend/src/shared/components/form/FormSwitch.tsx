import { forwardRef } from 'react'

export interface FormSwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
}

export const FormSwitch = forwardRef<HTMLInputElement, FormSwitchProps>(
  ({ className = '', error, ...props }, ref) => {
    return (
      <div className="flex items-center">
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            className="sr-only peer"
            ref={ref}
            {...props}
          />
          <div className={`w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-ring rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary ${error ? 'border-destructive' : ''} ${className}`}></div>
        </label>
      </div>
    )
  }
)
FormSwitch.displayName = 'FormSwitch'
