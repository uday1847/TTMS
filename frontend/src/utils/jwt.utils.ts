export interface JWTPayload {
  sub: string
  email: string
  roles?: string[]
  permissions?: string[]
  version?: number
  iss?: string
  aud?: string
  exp?: number
  [key: string]: any
}

export function decodeJWT(token: string): JWTPayload | null {
  try {
    const base64Url = token.split('.')[1]
    if (!base64Url) return null
    
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )

    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Failed to decode JWT:', error)
    return null
  }
}

export function isTokenValid(token: string | null): boolean {
  if (!token) return false;
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) return false;
  
  // Return true if expiration time is in the future
  return payload.exp * 1000 > Date.now();
}
