import { useTripHistory } from '../hooks/use-trips';
import { Loader2, Clock, CheckCircle2, XCircle, Truck, MapPin } from 'lucide-react';
import { TripStatus } from '../types/trip.types';

interface TripTimelineProps {
  tripId: string;
}

export function TripTimeline({ tripId }: TripTimelineProps) {
  const { data: response, isLoading, isError } = useTripHistory(tripId);

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isError || !response) {
    return (
      <div className="p-4 text-sm text-red-500 bg-red-50 rounded-md">
        Failed to load trip history.
      </div>
    );
  }

  const history = response;

  if (!history || history.length === 0) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        No history records found for this trip.
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case TripStatus.PENDING:
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case TripStatus.DISPATCHED:
        return <Truck className="h-4 w-4 text-blue-500" />;
      case TripStatus.IN_PROGRESS:
        return <MapPin className="h-4 w-4 text-purple-500" />;
      case TripStatus.COMPLETED:
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case TripStatus.CANCELLED:
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-8">
      {history.map((record, index) => (
        <div key={record.id} className="relative flex items-start space-x-4">
          {/* Connector Line */}
          {index !== history.length - 1 && (
            <div className="absolute left-4 top-8 -ml-px h-full w-0.5 bg-border" aria-hidden="true" />
          )}
          
          <div className="relative flex h-8 w-8 items-center justify-center rounded-full border bg-background shadow-sm">
            {getStatusIcon(record.new_status)}
          </div>
          
          <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
            <div>
              <p className="text-sm text-foreground font-medium">
                Status changed to <span className="font-semibold">{record.new_status.replace('_', ' ')}</span>
              </p>
              {record.remarks && (
                <p className="mt-1 text-sm text-muted-foreground">
                  {record.remarks}
                </p>
              )}
            </div>
            <div className="whitespace-nowrap text-right text-sm text-muted-foreground">
              <time dateTime={record.created_at}>
                {new Date(record.created_at).toLocaleString()}
              </time>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
