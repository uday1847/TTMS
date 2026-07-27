export interface ApiError {
  message: string;
  status?: number;
  success?: boolean;
  code?: string;
  errors?: Record<string, string[]>;
  raw?: unknown;
}
