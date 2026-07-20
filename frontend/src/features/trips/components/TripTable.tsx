import { useState } from 'react';
import { Link } from 'react-router';
import type { TripResponseDto } from '../types/trip.types';
import { TripStatusBadge } from './TripStatusBadge';
import { DeleteTripDialog } from './DeleteTripDialog';
import { TripStatusDialog } from './TripStatusDialog';
import { PermissionGuard } from '@/shared/auth';
import dayjs from 'dayjs';
import { MoreHorizontal, Edit, Eye, Trash2, Activity } from 'lucide-react';
import { Button } from '@/shared/ui/button/button';

interface TripTableProps {
  data: TripResponseDto[];
  isLoading?: boolean;
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(amount);
};

export function TripTable({ data, isLoading }: TripTableProps) {
  const [deleteTrip, setDeleteTrip] = useState<TripResponseDto | null>(null);
  const [statusTrip, setStatusTrip] = useState<TripResponseDto | null>(null);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="w-full h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="w-full h-64 flex flex-col items-center justify-center text-muted-foreground border rounded-md bg-card">
        <p>No trips found.</p>
      </div>
    );
  }

  const toggleMenu = (id: string) => {
    setOpenMenuId(openMenuId === id ? null : id);
  };

  return (
    <>
      <div className="overflow-x-auto rounded-lg border shadow-sm bg-card">
        <table className="w-full text-sm text-left text-muted-foreground">
          <thead className="text-xs text-foreground uppercase bg-muted/50 border-b">
            <tr>
              <th className="px-4 py-3 font-medium">Trip No</th>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Party / Driver</th>
              <th className="px-4 py-3 font-medium">Route</th>
              <th className="px-4 py-3 font-medium text-right">Freight</th>
              <th className="px-4 py-3 font-medium text-center">Status</th>
              <th className="px-4 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((trip) => (
              <tr key={trip.id} className="border-b hover:bg-muted/20">
                <td className="px-4 py-3 font-medium text-foreground whitespace-nowrap">
                  {trip.trip_number}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  {dayjs(trip.trip_date).format('DD MMM YYYY')}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-col">
                    <span className="font-semibold text-foreground">{trip.party_name}</span>
                    <span className="text-xs">{trip.driver_name}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-col text-xs space-y-1">
                    <span className="truncate max-w-[150px]">{trip.source_location}</span>
                    <span className="text-muted-foreground font-mono">↓</span>
                    <span className="truncate max-w-[150px]">{trip.destination_location}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex flex-col items-end">
                    <span className="font-medium text-foreground">{formatCurrency(trip.freight_amount)}</span>
                    <span className="text-xs text-green-600">Net: {formatCurrency(trip.net_profit || trip.freight_amount)}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <TripStatusBadge status={trip.status} />
                </td>
                <td className="px-4 py-3 text-right relative">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleMenu(trip.id)}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                  
                  {openMenuId === trip.id && (
                    <>
                      <div 
                        className="fixed inset-0 z-40" 
                        onClick={() => setOpenMenuId(null)}
                      ></div>
                      <div className="absolute right-8 top-10 z-50 w-48 bg-card border rounded-md shadow-lg py-1 text-left">
                        <Link 
                          to={`/trips/${trip.id}`}
                          className="flex items-center px-4 py-2 text-sm hover:bg-accent"
                          onClick={() => setOpenMenuId(null)}
                        >
                          <Eye className="mr-2 h-4 w-4" /> View Details
                        </Link>
                        
                        <PermissionGuard permission="trips:update">
                          <Link 
                            to={`/trips/${trip.id}/edit`}
                            className="flex items-center px-4 py-2 text-sm hover:bg-accent"
                            onClick={() => setOpenMenuId(null)}
                          >
                            <Edit className="mr-2 h-4 w-4" /> Edit Trip
                          </Link>
                          
                          <button
                            onClick={() => { setStatusTrip(trip); setOpenMenuId(null); }}
                            className="w-full flex items-center px-4 py-2 text-sm hover:bg-accent text-left"
                          >
                            <Activity className="mr-2 h-4 w-4" /> Update Status
                          </button>
                        </PermissionGuard>
                        
                        <PermissionGuard permission="trips:delete">
                          <button
                            onClick={() => { setDeleteTrip(trip); setOpenMenuId(null); }}
                            disabled={trip.status !== 'PENDING'}
                            className="w-full flex items-center px-4 py-2 text-sm hover:bg-accent text-destructive text-left disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Trash2 className="mr-2 h-4 w-4" /> Delete Trip
                          </button>
                        </PermissionGuard>
                      </div>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {deleteTrip && (
        <DeleteTripDialog
          tripId={deleteTrip.id}
          tripNumber={deleteTrip.trip_number}
          isOpen={!!deleteTrip}
          onClose={() => setDeleteTrip(null)}
        />
      )}

      {statusTrip && (
        <TripStatusDialog
          trip={statusTrip}
          isOpen={!!statusTrip}
          onClose={() => setStatusTrip(null)}
        />
      )}
    </>
  );
}
