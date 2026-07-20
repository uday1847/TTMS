import type { ReactNode } from 'react'

interface FormActionsProps {
  children: ReactNode
  className?: string
}

export function FormActions({ children, className = '' }: FormActionsProps) {
  return (
    <div className={`flex items-center justify-end space-x-2 pt-4 border-t border-border mt-6 ${className}`}>
      {children}
    </div>
  )
}
