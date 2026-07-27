import { z } from 'zod';
import { PartyType } from '../types/party.types';

export const mobileRegex = /^\+?[0-9\-\s]+$/;
export const gstRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
export const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

export const partySchema = z.object({
  name: z.string()
    .min(3, 'Name must be at least 3 characters')
    .max(100, 'Name must be less than 100 characters'),
  party_type: z.nativeEnum(PartyType, {
    error: 'Please select a valid party type',
  }),
  mobile_number: z.string()
    .min(10, 'Mobile number must be at least 10 digits')
    .max(20, 'Mobile number must be less than 20 characters')
    .regex(mobileRegex, 'Invalid mobile number format'),
  alternate_mobile: z.string()
    .regex(mobileRegex, 'Invalid mobile number format')
    .max(20, 'Alternate mobile must be less than 20 characters')
    .optional()
    .or(z.literal('')),
  email: z.string()
    .email('Invalid email format')
    .max(255, 'Email must be less than 255 characters')
    .optional()
    .or(z.literal('')),
  gst_number: z.string()
    .regex(gstRegex, 'Invalid Indian GSTIN format')
    .optional()
    .or(z.literal('')),
  pan_number: z.string()
    .regex(panRegex, 'Invalid Indian PAN format')
    .optional()
    .or(z.literal('')),
  address: z.string().optional(),
  city: z.string().max(100, 'City must be less than 100 characters').optional(),
  state: z.string().max(100, 'State must be less than 100 characters').optional(),
  pincode: z.string().max(20, 'Pincode must be less than 20 characters').optional(),
  contact_person: z.string().max(100, 'Contact person must be less than 100 characters').optional(),
  opening_balance: z.number().min(0, 'Opening balance cannot be negative').optional(),
  credit_limit: z.number().min(0, 'Credit limit cannot be negative').optional(),
  remarks: z.string().max(500, 'Remarks must be less than 500 characters').optional(),
});

export type PartyFormData = z.infer<typeof partySchema>;
