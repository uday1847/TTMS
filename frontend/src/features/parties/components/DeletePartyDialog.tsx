import { useDeleteParty } from '../hooks/use-parties';
import { useNotificationStore } from '@/stores/notification-store';
import { Loader2 } from 'lucide-react';
import { showApiError } from '@/shared/error';

interface DeletePartyDialogProps {
  partyId: string;
  partyName: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function DeletePartyDialog({
  partyId,
  partyName,
  isOpen,
  onClose,
  onSuccess,
}: DeletePartyDialogProps) {
  const { mutateAsync: deleteParty, isPending } = useDeleteParty();
  const { addNotification } = useNotificationStore();

  if (!isOpen) return null;

  const handleDelete = async () => {
    try {
      await deleteParty(partyId);
      addNotification({
        type: 'success',
        title: 'Party Deleted',
        message: `Party ${partyName} has been successfully deleted.`,
      });
      onSuccess?.();
      onClose();
    } catch (error: any) {
      showApiError(error, 'Failed to delete party');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="w-full max-w-md bg-card rounded-lg shadow-xl overflow-hidden border">
        <div className="p-6">
          <h3 className="text-lg font-medium">Are you absolutely sure?</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            This party will be soft deleted. If it is linked to active trips, deletion will be blocked.
            <span className="font-semibold text-foreground"> {partyName}</span> will be marked as deleted.
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
            Delete Party
          </button>
        </div>
      </div>
    </div>
  );
}
