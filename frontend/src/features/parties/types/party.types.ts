export const PartyType = {
  CUSTOMER: 'CUSTOMER',
  SUPPLIER: 'SUPPLIER',
  BROKER: 'BROKER',
  OTHER: 'OTHER',
} as const;

export type PartyType = typeof PartyType[keyof typeof PartyType];

export interface PartyResponseDto {
  id: string;
  name: string;
  party_type: PartyType;
  mobile_number: string;
  alternate_mobile?: string | null;
  email?: string | null;
  gst_number?: string | null;
  pan_number?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  pincode?: string | null;
  contact_person?: string | null;
  opening_balance: number;
  credit_limit: number;
  remarks?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PartyCreateDto {
  name: string;
  party_type: PartyType | '';
  mobile_number: string;
  alternate_mobile?: string;
  email?: string;
  gst_number?: string;
  pan_number?: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  contact_person?: string;
  opening_balance?: number;
  credit_limit?: number;
  remarks?: string;
}

export interface PartyUpdateDto extends Partial<PartyCreateDto> {
  is_active?: boolean;
}
