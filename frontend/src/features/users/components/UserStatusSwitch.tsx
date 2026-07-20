import { FormSwitch } from '@/shared/components/form'
import { useToggleUserStatus } from '../hooks/use-toggle-user-status'

interface UserStatusSwitchProps {
  userId: string
  isActive: boolean
  disabled?: boolean
}

export function UserStatusSwitch({ userId, isActive, disabled }: UserStatusSwitchProps) {
  const { mutate, isPending } = useToggleUserStatus()

  return (
    <FormSwitch
      checked={isActive}
      disabled={disabled || isPending}
      onChange={(e) => {
        mutate({ id: userId, isActive: e.target.checked })
      }}
    />
  )
}
