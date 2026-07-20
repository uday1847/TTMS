import { useState } from 'react';
import { useUpdateTripStatus } from '../hooks/use-trips';
import type { TripResponseDto } from '../types/trip.types';
import { TripStatus } from '../types/trip.types';
import { useNotificationStore } from '@/stores/notification-store';
import { Loader2 } from 'lucide-react';

interface TripStatusDialogProps {
  trip: TripResponseDto;
  isOpen: boolean;
  onClose: () => void;
}

export function TripStatusDialog({ trip, isOpen, onClose }: TripStatusDialogProps) {
  const { mutateAsync: updateStatus, isPending } = useUpdateTripStatus(trip.id);
  const { addNotification } = useNotificationStore();
  const [status, setStatus] = useState<TripStatus>(trip.status);
  const [remarks, setRemarks] = useState('');

  if (!isOpen) return null;

  // Determine allowed transitions
  const allowedStatuses = (() => {
    switch (trip.status) {
      case 'PENDING':
        return [TripStatus.DISPATCHED, TripStatus.CANCELLED];
      case 'DISPATCHED':
        return [TripStatus.IN_PROGRESS, TripStatus.CANCELLED];
      case 'IN_PROGRESS':
        return [TripStatus.COMPLETED, TripStatus.CANCELLED];
      case 'COMPLETED':
      case 'CANCELLED':
        return [];
      default:
        return [];
    }
  })();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await updateStatus({ status, remarks: remarks || undefined });
      addNotification({
        type: 'success',
        title: 'Status Updated',
        message: `Trip ${trip.trip_number} status updated to ${status}.`
      });
      onClose();
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error.response?.data?.detail || 'Failed to update trip status.'
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="w-full max-w-md bg-card rounded-lg shadow-xl overflow-hidden border">
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-4">
            <h3 className="text-lg font-medium">Update Trip Status</h3>
            <p className="text-sm text-muted-foreground">
              Current status: <span className="font-semibold text-foreground">{trip.status}</span>
            </p>

            <div className="space-y-2">
              <label className="text-sm font-medium">New Status</label>
              <select
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={status}
                onChange={(e) => setStatus(e.target.value as TripStatus)}
                disabled={isPending || allowedStatuses.length === 0}
              >
                <option value={trip.status} disabled>Select next status...</option>
                {allowedStatuses.map((s) => (
                  <option key={s} value={s}>{s.replace('_', ' ')}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Remarks (Optional)</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Reason for status change..."
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                disabled={isPending || allowedStatuses.length === 0}
              />
            </div>
          </div>
          
          <div className="px-6 py-4 bg-muted/50 flex justify-end space-x-3 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium border rounded-md hover:bg-accent focus:outline-none"
              disabled={isPending}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-primary-foreground bg-primary rounded-md hover:bg-primary/90 focus:outline-none flex items-center disabled:opacity-50"
              disabled={isPending || status === trip.status || allowedStatuses.length === 0}
            >
              {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Update Status
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
