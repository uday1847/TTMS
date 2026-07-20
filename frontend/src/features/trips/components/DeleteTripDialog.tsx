import { useDeleteTrip } from '../hooks/use-trips';
import { useNotificationStore } from '@/stores/notification-store';
import { Loader2 } from 'lucide-react';

interface DeleteTripDialogProps {
  tripId: string;
  tripNumber: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function DeleteTripDialog({
  tripId,
  tripNumber,
  isOpen,
  onClose,
  onSuccess,
}: DeleteTripDialogProps) {
  const { mutateAsync: deleteTrip, isPending } = useDeleteTrip();
  const { addNotification } = useNotificationStore();

  if (!isOpen) return null;

  const handleDelete = async () => {
    try {
      await deleteTrip(tripId);
      addNotification({
        type: 'success',
        title: 'Trip Deleted',
        message: `Trip ${tripNumber} has been successfully deleted.`,
      });
      onSuccess?.();
      onClose();
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Failed to delete trip',
        message: error.response?.data?.detail || error.message || 'An error occurred',
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="w-full max-w-md bg-card rounded-lg shadow-xl overflow-hidden border">
        <div className="p-6">
          <h3 className="text-lg font-medium">Are you absolutely sure?</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            This action cannot be undone. This will permanently delete the trip
            <span className="font-semibold text-foreground"> {tripNumber}</span>. Note that only PENDING trips without
            associated expenses or invoices can be deleted.
          </p>
        </div>
        <div className="px-6 py-4 bg-muted/50 flex justify-end space-x-3 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium border rounded-md hover:bg-accent focus:outline-none"
            disabled={isPending}
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            className="px-4 py-2 text-sm font-medium text-destructive-foreground bg-destructive rounded-md hover:bg-destructive/90 focus:outline-none flex items-center"
            disabled={isPending}
          >
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Delete Trip
          </button>
        </div>
      </div>
    </div>
  );
}
