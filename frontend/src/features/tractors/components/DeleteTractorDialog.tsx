import { Loader2 } from 'lucide-react';
import { useDeleteTractor } from '../hooks/use-tractors';
import type { TractorResponseDto } from '../types/tractor.types';
import { showApiError } from '@/shared/error';

interface DeleteTractorDialogProps {
  tractor: TractorResponseDto;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function DeleteTractorDialog({ tractor, isOpen, onClose, onSuccess }: DeleteTractorDialogProps) {
  const deleteTractor = useDeleteTractor();

  if (!isOpen) return null;

  const handleDelete = async () => {
    try {
      await deleteTractor.mutateAsync(tractor.id);
      if (onSuccess) onSuccess();
      onClose();
    } catch (error: any) {
      showApiError(error, 'Failed to delete tractor');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="w-full max-w-md bg-white rounded-lg shadow-xl overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-medium text-gray-900">Delete Tractor</h3>
          <p className="mt-2 text-sm text-gray-500">
            Are you sure you want to delete the tractor <span className="font-semibold">{tractor.tractor_number}</span>? This action can only be reversed by an administrator.
          </p>
        </div>
        <div className="px-6 py-4 bg-gray-50 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={deleteTractor.isPending}
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 flex items-center"
            disabled={deleteTractor.isPending}
          >
            {deleteTractor.isPending && (
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
