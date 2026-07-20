import { z } from 'zod'

export const driverSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  address: z.string().optional().nullable(),
  employeeCode: z.string().min(1, 'Employee code is required'),
  licenseNumber: z.string().min(1, 'License number is required'),
  licenseExpiry: z.string().min(1, 'License expiry is required'),
  licenseClass: z.string().min(1, 'License class is required'),
  contactPhone: z.string().min(1, 'Contact phone is required'),
  emergencyContactPhone: z.string().optional().nullable(),
  fixedSalary: z.coerce.number().min(0).optional(),
  commissionPercentage: z.coerce.number().min(0).max(100).optional(),
  driverType: z.string().min(1, 'Driver type is required'),
  currentStatus: z.enum(['available', 'on_trip', 'on_leave', 'inactive']).optional(),
}).refine((data) => {
  if (data.emergencyContactPhone && data.contactPhone === data.emergencyContactPhone) {
    return false
  }
  return true
}, {
  message: "Emergency contact phone cannot be the same as primary contact phone",
  path: ["emergencyContactPhone"]
})

export type DriverFormValues = z.infer<typeof driverSchema>
