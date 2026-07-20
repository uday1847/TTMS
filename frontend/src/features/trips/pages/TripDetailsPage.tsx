import { useParams, useNavigate } from 'react-router';
import { useTrip } from '../hooks/use-trips';
import { Button } from '@/shared/ui/button/button';
import { TripStatusBadge } from '../components/TripStatusBadge';
import { PermissionGuard } from '@/shared/auth';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card/card';
import { Loader2, ArrowLeft, Edit, History, MapPin, Navigation, Truck, User, Building, Receipt } from 'lucide-react';
import dayjs from 'dayjs';

export default function TripDetailsPage() {
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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/trips')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{trip.trip_number}</h1>
            <div className="flex items-center space-x-2 mt-1">
              <TripStatusBadge status={trip.status} />
              <span className="text-sm text-muted-foreground">
                Created on {dayjs(trip.created_at).format('MMMM D, YYYY')}
              </span>
            </div>
          </div>
        </div>
        <div className="flex space-x-2">
          <PermissionGuard permission="trips:read">
            <Button variant="outline" onClick={() => navigate(`/trips/${trip.id}/history`)}>
              <History className="mr-2 h-4 w-4" />
              History
            </Button>
          </PermissionGuard>
          <PermissionGuard permission="trips:update">
            <Button variant="outline" onClick={() => navigate(`/trips/${trip.id}/edit`)}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
          </PermissionGuard>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Route Details */}
        <Card className="col-span-1 md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <MapPin className="mr-2 h-5 w-5 text-muted-foreground" /> Route Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
              <div className="space-y-1 w-5/12">
                <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Origin</p>
                <p className="text-lg font-semibold">{trip.source_location}</p>
                <p className="text-sm text-muted-foreground">
                  Departure: {dayjs(trip.trip_date).format('MMMM D, YYYY')}
                </p>
              </div>
              <div className="flex-1 flex flex-col items-center justify-center px-4">
                <Navigation className="h-6 w-6 text-primary mb-2 rotate-90" />
                <div className="w-full border-t-2 border-dashed border-primary/30"></div>
              </div>
              <div className="space-y-1 w-5/12 text-right">
                <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Destination</p>
                <p className="text-lg font-semibold">{trip.destination_location}</p>
                <p className="text-sm text-muted-foreground">
                  ETA: {dayjs(trip.expected_delivery_date).format('MMMM D, YYYY')}
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
               <div>
                 <p className="text-sm text-muted-foreground mb-1">Actual Delivery</p>
                 <p className="font-medium">{trip.actual_delivery_date ? dayjs(trip.actual_delivery_date).format('MMMM D, YYYY') : 'Pending'}</p>
               </div>
               <div>
                 <p className="text-sm text-muted-foreground mb-1">Trip Age</p>
                 <p className="font-medium">{trip.trip_age ?? 0} days</p>
               </div>
               <div>
                 <p className="text-sm text-muted-foreground mb-1">Status Remarks</p>
                 <p className="font-medium">{trip.remarks || 'None'}</p>
               </div>
            </div>
          </CardContent>
        </Card>

        {/* Financial Summary */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Receipt className="mr-2 h-5 w-5 text-muted-foreground" /> Financials
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-muted-foreground">Freight Revenue</span>
              <span className="font-semibold text-green-600">{formatCurrency(trip.freight_amount)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-muted-foreground">Advance Paid</span>
              <span className="font-medium">{formatCurrency(trip.advance_amount)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-muted-foreground">Total Expenses</span>
              <span className="font-medium text-red-600">{formatCurrency(trip.total_expense || 0)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-muted-foreground">Fuel Cost</span>
              <span className="font-medium">{formatCurrency(trip.total_fuel_amount || 0)}</span>
            </div>
            <div className="flex justify-between items-center pt-2">
              <span className="text-base font-medium">Est. Net Profit</span>
              <span className={`text-lg font-bold ${trip.net_profit && trip.net_profit > 0 ? 'text-green-600' : ''}`}>
                {formatCurrency(trip.net_profit || trip.freight_amount)}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Asset Assignments */}
        <Card className="col-span-1 md:col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Truck className="mr-2 h-5 w-5 text-muted-foreground" /> Assignments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex items-start space-x-4 p-4 border rounded-lg bg-card">
                <Building className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Customer / Party</p>
                  <p className="text-lg font-semibold mt-1">{trip.party_name}</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 p-4 border rounded-lg bg-card">
                <Truck className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Assigned Tractor</p>
                  <p className="text-lg font-semibold mt-1">{trip.tractor_number}</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 p-4 border rounded-lg bg-card">
                <User className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Assigned Driver</p>
                  <p className="text-lg font-semibold mt-1">{trip.driver_name}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
