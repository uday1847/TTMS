import { useNotificationStore } from '@/stores/notification-store';
import type { ApiError } from './api-error';

export function showApiError(error: ApiError | unknown, title = 'Operation Failed') {
  // If it's already structured as ApiError, it should have a message property
  const errorMessage = (error as ApiError)?.message || 'An unexpected error occurred.';
  
  useNotificationStore.getState().addNotification({
    type: 'error',
    title,
    message: errorMessage,
  });
}
