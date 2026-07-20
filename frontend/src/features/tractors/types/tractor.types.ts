export type TractorStatusDto = 'active' | 'in_maintenance' | 'out_of_service';

export interface TractorResponseDto {
  id: string;
  tractor_number: string;
  owner_name: string;
  rc_number: string;
  insurance_number: string | null;
  insurance_expiry: string;
  manufacturer: string | null;
  model: string | null;
  registration_date: string | null;
  remarks: string | null;
  status: TractorStatusDto;
  current_odometer: number;
  fuel_capacity: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  total_fuel_amount: number;
  average_kmpl: number | null;
}

export interface CreateTractorDto {
  tractor_number: string;
  owner_name: string;
  rc_number: string;
  insurance_number?: string | null;
  insurance_expiry: string;
  manufacturer?: string | null;
  model?: string | null;
  registration_date?: string | null;
  remarks?: string | null;
  fuel_capacity?: number | null;
}

export interface UpdateTractorDto extends Partial<CreateTractorDto> {
  is_active?: boolean;
}

export interface TractorListResponseDto {
  items: TractorResponseDto[];
  total: number;
  page: number;
  size: number;
}
