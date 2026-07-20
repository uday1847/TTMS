import { z } from 'zod';

export const tractorSchema = z.object({
  tractor_number: z.string().min(3, 'Tractor number must be at least 3 characters').max(30),
  owner_name: z.string().min(2, 'Owner name must be at least 2 characters').max(100),
  rc_number: z.string().min(5, 'RC number must be at least 5 characters').max(50),
  insurance_number: z.string().max(100).optional().nullable(),
  insurance_expiry: z.string().min(1, 'Insurance expiry is required').refine((val) => {
    // Backend validation requires insurance expiry >= today
    const selectedDate = new Date(val);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return selectedDate >= today;
  }, {
    message: 'Tractor insurance has already expired',
  }),
  manufacturer: z.string().max(50).optional().nullable(),
  model: z.string().max(50).optional().nullable(),
  registration_date: z.string().optional().nullable(),
  remarks: z.string().max(500).optional().nullable(),
  fuel_capacity: z.preprocess((val) => val === '' || val === null ? undefined : Number(val), z.number().positive().max(2000).optional()),
});

export type TractorFormValues = z.infer<typeof tractorSchema>;
