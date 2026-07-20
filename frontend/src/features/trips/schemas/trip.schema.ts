import { z } from 'zod';
import { TripStatus } from '../types/trip.types';

export const tripSchema = z.object({
  party_id: z.string().uuid('Please select a party'),
  tractor_id: z.string().uuid('Please select a tractor'),
  driver_id: z.string().uuid('Please select a driver'),
  source_location: z.string().min(2, 'Source must be at least 2 characters').max(100, 'Source must be at most 100 characters'),
  destination_location: z.string().min(2, 'Destination must be at least 2 characters').max(100, 'Destination must be at most 100 characters'),
  trip_date: z.string().min(1, 'Trip date is required'),
  expected_delivery_date: z.string().min(1, 'Expected delivery date is required'),
  freight_amount: z.coerce.number().min(0.01, 'Freight amount must be greater than 0'),
  advance_amount: z.coerce.number().min(0, 'Advance amount cannot be negative').default(0),
  remarks: z.string().max(500, 'Remarks cannot exceed 500 characters').optional().nullable(),
}).refine(
  (data) => data.advance_amount <= data.freight_amount,
  {
    message: "Advance amount cannot exceed the freight amount",
    path: ["advance_amount"]
  }
).refine(
  (data) => {
    const tripDate = new Date(data.trip_date);
    const expectedDelivery = new Date(data.expected_delivery_date);
    return expectedDelivery >= tripDate;
  },
  {
    message: "Expected delivery date cannot be before the trip date",
    path: ["expected_delivery_date"]
  }
);

export type TripFormData = z.infer<typeof tripSchema>;

export const tripStatusSchema = z.object({
  status: z.nativeEnum(TripStatus),
  remarks: z.string().max(500, 'Remarks cannot exceed 500 characters').optional().nullable(),
});

export type TripStatusFormData = z.infer<typeof tripStatusSchema>;
