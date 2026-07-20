import { z } from 'zod';

export const userSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters').max(50, 'Username cannot exceed 50 characters'),
  password: z.string().min(8, 'Password must be at least 8 characters').optional(),
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  phone: z.string().optional(),
  roleIds: z.array(z.string().uuid('Invalid role ID')).optional(),
  isActive: z.boolean().optional(),
});

export type UserFormValues = z.infer<typeof userSchema>;
