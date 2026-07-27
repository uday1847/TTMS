export type DriverStatus = 'available' | 'on_trip' | 'on_leave' | 'inactive';

export interface DriverResponseDto {
  id: string;
  name: string;
  address?: string | null;
  userId?: string | null;
  employeeCode: string;
  licenseNumber: string;
  licenseExpiry: string;
  licenseClass: string;
  contactPhone: string;
  emergencyContactPhone?: string | null;
  fixedSalary: number;
  commissionPercentage: number;
  driverType: string;
  currentStatus: DriverStatus;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string | null;
  createdBy?: string | null;
  updatedBy?: string | null;
  versionId: number;
}

export interface DriverCreateDto {
  name: string;
  userId?: string | null;
  address?: string | null;
  employeeCode: string;
  licenseNumber: string;
  licenseExpiry: string;
  licenseClass: string;
  contactPhone: string;
  emergencyContactPhone?: string | null;
  fixedSalary?: number;
  commissionPercentage?: number;
  driverType: string;
  currentStatus?: DriverStatus;
}

export interface DriverUpdateDto extends Partial<DriverCreateDto> {
  isActive?: boolean;
}
