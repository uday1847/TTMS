export const TripStatus = {
  PENDING: 'PENDING',
  DISPATCHED: 'DISPATCHED',
  IN_PROGRESS: 'IN_PROGRESS',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED'
} as const;

export type TripStatus = typeof TripStatus[keyof typeof TripStatus];

export interface TripResponseDto {
  id: string;
  trip_number: string;
  party_id: string;
  tractor_id: string;
  driver_id: string;
  source_location: string;
  destination_location: string;
  trip_date: string;
  expected_delivery_date: string;
  actual_delivery_date: string | null;
  freight_amount: number;
  advance_amount: number;
  remarks: string | null;
  status: TripStatus;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  
  // Computed fields
  driver_name: string | null;
  tractor_number: string | null;
  party_name: string | null;
  trip_age: number | null;
  status_label: string | null;
  total_expense: number | null;
  net_profit: number | null;
  total_advances: number | null;
  expense_count: number | null;
  total_fuel_amount: number | null;
  fuel_transaction_count: number | null;
}

export interface TripCreateDto {
  party_id: string;
  tractor_id: string;
  driver_id: string;
  source_location: string;
  destination_location: string;
  trip_date: string;
  expected_delivery_date: string;
  freight_amount: number;
  advance_amount: number;
  remarks?: string | null;
}

export interface TripUpdateDto extends Partial<TripCreateDto> {
  actual_delivery_date?: string;
  is_active?: boolean;
}

export interface TripStatusUpdateDto {
  status: TripStatus;
  remarks?: string | null;
}

export interface TripStatusHistoryResponseDto {
  id: string;
  old_status: string | null;
  new_status: string;
  remarks: string | null;
  created_by: string | null;
  created_at: string;
}
