import { useState } from 'react';
import { useUpdatePartyStatus } from '../hooks/use-parties';
import { showApiError } from '@/shared/error';
import { useNotificationStore } from '@/stores/notification-store';
import { Loader2 } from 'lucide-react';

interface PartyStatusSwitchProps {
  partyId: string;
  initialStatus: boolean;
  disabled?: boolean;
}

export function PartyStatusSwitch({ partyId, initialStatus, disabled }: PartyStatusSwitchProps) {
  const [isActive, setIsActive] = useState(initialStatus);
  const { mutateAsync: updateStatus, isPending } = useUpdatePartyStatus(partyId);
  const { addNotification } = useNotificationStore();

  const handleToggle = async () => {
    const newStatus = !isActive;
    setIsActive(newStatus); // Optimistic UI update

    try {
      await updateStatus(newStatus);
      addNotification({
        type: 'success',
        title: 'Status Updated',
        message: `Party is now ${newStatus ? 'active' : 'inactive'}.`,
      });
    } catch (error: any) {
      showApiError(error, 'Failed to update party status');
    }
  };

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isActive}
      disabled={disabled || isPending}
      onClick={handleToggle}
      className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 ${
        isActive ? 'bg-primary' : 'bg-input'
      }`}
    >
      <span
        className={`pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform ${
          isActive ? 'translate-x-5' : 'translate-x-0'
        } ${isPending ? 'flex items-center justify-center' : ''}`}
      >
        {isPending && <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />}
      </span>
    </button>
  );
}
