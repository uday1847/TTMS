import { useState } from 'react';
import { useUpdateTractorStatus } from '../hooks/use-tractors';
import { showApiError } from '@/shared/error';
import type { TractorResponseDto } from '../types/tractor.types';

interface TractorStatusSwitchProps {
  tractor: TractorResponseDto;
}

export function TractorStatusSwitch({ tractor }: TractorStatusSwitchProps) {
  const [isActive, setIsActive] = useState(tractor.is_active);
  const updateStatus = useUpdateTractorStatus();

  const toggleStatus = async () => {
    const newStatus = !isActive;
    setIsActive(newStatus);
    
    try {
      await updateStatus.mutateAsync({
        id: tractor.id,
        isActive: newStatus,
      });
    } catch (error: any) {
      setIsActive(tractor.is_active);
      showApiError(error, 'Failed to update status');
    }
  };

  return (
    <button
      onClick={toggleStatus}
      disabled={updateStatus.isPending}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        isActive ? 'bg-blue-600' : 'bg-gray-200'
      } ${updateStatus.isPending ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      role="switch"
      aria-checked={isActive}
    >
      <span className="sr-only">Toggle tractor status</span>
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          isActive ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );
}
