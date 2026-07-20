import { useUpdateDriverStatus } from '../hooks/use-drivers'

interface DriverStatusSwitchProps {
  id: string
  isActive: boolean
  disabled?: boolean
}

export function DriverStatusSwitch({ id, isActive, disabled }: DriverStatusSwitchProps) {
  const { mutate: updateStatus, isPending } = useUpdateDriverStatus()

  return (
    <label className="relative inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        className="sr-only peer"
        checked={isActive}
        disabled={disabled || isPending}
        onChange={(e) => updateStatus({ id, isActive: e.target.checked })}
      />
      <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600 disabled:opacity-50"></div>
    </label>
  )
}
