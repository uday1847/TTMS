import { useParams, useNavigate } from 'react-router';
import { useTrip, useUpdateTrip } from '../hooks/use-trips';
import { showApiError } from '@/shared/error';
import { TripForm } from '../components/TripForm';
import { useNotificationStore } from '@/stores/notification-store';
import { Loader2 } from 'lucide-react';
import type { TripFormData } from '../schemas/trip.schema';

export default function TripEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addNotification } = useNotificationStore();

  const { data: response, isLoading, isError } = useTrip(id!);
  const { mutateAsync: updateTrip, isPending } = useUpdateTrip(id!);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isError || !response) {
    return (
      <div className="text-center p-8 text-red-500">
        Failed to load trip details.
      </div>
    );
  }

  const trip = response;

  const handleSubmit = async (data: TripFormData) => {
    try {
      await updateTrip(data);
      addNotification({
        type: 'success',
        title: 'Trip Updated',
        message: 'Trip details have been successfully updated.',
      });
      navigate('/trips');
    } catch (error: any) {
      showApiError(error, 'Failed to update trip');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Edit Trip: {trip.trip_number}</h1>
        <p className="text-muted-foreground">Modify dispatch and routing details.</p>
      </div>

      <div className="p-6 bg-card border rounded-xl shadow-sm">
        <TripForm
          initialData={trip}
          onSubmit={handleSubmit}
          isLoading={isPending}
          onCancel={() => navigate('/trips')}
        />
      </div>
    </div>
  );
}
