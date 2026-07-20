import { TripStatus } from '../types/trip.types';

interface TripStatusBadgeProps {
  status: TripStatus;
}

export function TripStatusBadge({ status }: TripStatusBadgeProps) {
  const getBadgeStyles = () => {
    switch (status) {
      case TripStatus.PENDING:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case TripStatus.DISPATCHED:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case TripStatus.IN_PROGRESS:
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case TripStatus.COMPLETED:
        return 'bg-green-100 text-green-800 border-green-200';
      case TripStatus.CANCELLED:
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formattedStatus = status.replace('_', ' ').charAt(0) + status.replace('_', ' ').slice(1).toLowerCase();

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeStyles()}`}
    >
      {formattedStatus}
    </span>
  );
}
