import { TripForm } from '../components/TripForm';
import { useCreateTrip } from '../hooks/use-trips';
import { showApiError } from '@/shared/error';
import { useNotificationStore } from '@/stores/notification-store';
import { useNavigate } from 'react-router';
import type { TripFormData } from '../schemas/trip.schema';

export default function TripCreatePage() {
  const { mutateAsync: createTrip, isPending } = useCreateTrip();
  const { addNotification } = useNotificationStore();
  const navigate = useNavigate();

  const handleSubmit = async (data: TripFormData) => {
    try {
      await createTrip(data);
      addNotification({
        type: 'success',
        title: 'Trip Created',
        message: 'New trip has been successfully scheduled.',
      });
      navigate('/trips');
    } catch (error: any) {
      showApiError(error, 'Failed to create trip');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Schedule New Trip</h1>
        <p className="text-muted-foreground">Assign driver, tractor, and party for a new delivery.</p>
      </div>

      <div className="p-6 bg-card border rounded-xl shadow-sm">
        <TripForm onSubmit={handleSubmit} isLoading={isPending} onCancel={() => navigate('/trips')} />
      </div>
    </div>
  );
}
