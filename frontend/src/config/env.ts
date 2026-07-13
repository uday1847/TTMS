import { z } from 'zod'

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url().default('http://localhost:8000/api'),
  VITE_APP_NAME: z.string().default('TTMS'),
  VITE_APP_VERSION: z.string().default('1.0.0'),
  MODE: z.enum(['development', 'production', 'test']).default('development'),
})

const parsedEnv = envSchema.safeParse({
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  VITE_APP_NAME: import.meta.env.VITE_APP_NAME,
  VITE_APP_VERSION: import.meta.env.VITE_APP_VERSION,
  MODE: import.meta.env.MODE,
})

if (!parsedEnv.success) {
  console.error('❌ Invalid environment configuration:', parsedEnv.error.format())
  throw new Error('Invalid environment configuration')
}

export const env = parsedEnv.data
