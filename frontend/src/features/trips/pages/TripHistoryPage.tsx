import { useParams, useNavigate } from 'react-router';
import { useTrip } from '../hooks/use-trips';
import { TripTimeline } from '../components/TripTimeline';
import { Button } from '@/shared/ui/button/button';
import { TripStatusBadge } from '../components/TripStatusBadge';
import { Loader2, ArrowLeft, History } from 'lucide-react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card/card';

export default function TripHistoryPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: response, isLoading, isError } = useTrip(id!);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isError || !response) {
    return (
      <div className="text-center p-8 text-red-500 bg-red-50 rounded-md">
        Failed to load trip details.
      </div>
    );
  }

  const trip = response;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(`/trips/${trip.id}`)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Timeline: {trip.trip_number}</h1>
          <div className="flex items-center space-x-2 mt-1">
            <span className="text-sm text-muted-foreground">Current Status:</span>
            <TripStatusBadge status={trip.status} />
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <History className="mr-2 h-5 w-5 text-muted-foreground" /> Audit Trail
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Chronological history of state transitions for this trip.
          </p>
        </CardHeader>
        <CardContent className="pt-6">
          <TripTimeline tripId={trip.id} />
        </CardContent>
      </Card>
    </div>
  );
}
