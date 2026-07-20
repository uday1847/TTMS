# TTMS Backend Audit Report

## Executive Summary
- Overall health score: 54/100
- Critical issues count: 4
- High issues count: 7
- Medium issues count: 9
- Low issues count: 5

## Architecture Overview
- Detected modules:
  - API layer: [backend/app/api](backend/app/api)
  - Application services: [backend/app/application](backend/app/application)
  - Domain entities and exceptions: [backend/app/domain](backend/app/domain)
  - Infrastructure repositories and DB session setup: [backend/app/infrastructure](backend/app/infrastructure)
  - Core settings/security utilities: [backend/app/core](backend/app/core)
- Layer structure:
  - API routers depend on application services
  - Services depend on repositories and domain entities
  - Repositories wrap async SQLAlchemy sessions
  - DTOs are used at the application boundary for request/response serialization
- Dependency flow:
  - Request -> FastAPI router -> service -> repository -> async DB session -> PostgreSQL

## Critical Findings

### 1. Startup and router registration is brittle
- File path: [backend/app/main.py](backend/app/main.py), [backend/app/api/router.py](backend/app/api/router.py)
- Code snippet:
  - [backend/app/api/router.py](backend/app/api/router.py) includes the auth router twice.
  - [backend/app/main.py](backend/app/main.py) wires the central router and startup lifespan, but the runtime route inventory only exposed docs and health endpoints in the verification run.
- Root cause:
  - There is duplicate router inclusion for auth and a startup path that depends on database state during import/lifespan initialization.
  - The router tree is not stable enough to trust startup-time registration in the current environment.
- Risk:
  - API routes may not be reachable or may be registered inconsistently depending on import order and initialization state.
- Recommended fix:
  - Remove duplicate includes, verify router registration in a clean startup test, and ensure app startup fails clearly if configuration or DB prerequisites are missing.
- Estimated effort: Medium

### 2. Authentication uses hardcoded fallback JWT secrets
- File path: [backend/app/core/security.py](backend/app/core/security.py)
- Code snippet:
  - `JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-ttms-key-must-change-in-prod")`
- Root cause:
  - A hardcoded fallback secret is used when the environment variable is absent.
- Risk:
  - Tokens can be forged or accepted unpredictably in non-production environments and the app becomes insecure by default.
- Recommended fix:
  - Require `JWT_SECRET_KEY` from the environment and fail startup if it is missing or still uses the default placeholder.
- Estimated effort: Low

### 3. Default admin password is hardcoded in settings
- File path: [backend/app/core/settings.py](backend/app/core/settings.py)
- Code snippet:
  - `DEFAULT_ADMIN_PASSWORD: str = "Admin@123"`
- Root cause:
  - Seeded admin accounts inherit a known password unless overridden.
- Risk:
  - Immediate credential compromise if seeding is enabled or the environment is misconfigured.
- Recommended fix:
  - Remove the hardcoded default and require a strong runtime secret for initial bootstrap.
- Estimated effort: Low

### 4. CORS is configured with credentials and wildcard-like origin usage is not fully constrained
- File path: [backend/app/main.py](backend/app/main.py)
- Code snippet:
  - `allow_origins=settings.BACKEND_CORS_ORIGINS`
  - `allow_credentials=True`
- Root cause:
  - The code uses environment-driven origins but the settings default already includes localhost origins only; the current configuration does not explicitly restrict origins to the exact expected frontend deployment values.
- Risk:
  - If the environment is misconfigured, browsers may reject requests or allow unintended origins that do not match the frontend deployment.
- Recommended fix:
  - Define an explicit allowlist for all frontend deployments and make it mandatory in production.
- Estimated effort: Low

## CORS Analysis
- Middleware configuration:
  - CORS middleware is registered in [backend/app/main.py](backend/app/main.py).
  - Current settings use `settings.BACKEND_CORS_ORIGINS`.
  - `allow_credentials=True` is enabled.
  - Methods allowed: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`.
  - Headers allowed: `Authorization`, `Content-Type`, `Accept`, `Origin`, `X-Requested-With`.
- Exact frontend origins currently allowed by default:
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`
- Recommended secure configuration:
  - Keep `allow_credentials=True` only if a strict allowlist of known frontend origins is present.
  - Add deployment-specific origins such as the production frontend domain explicitly.
  - Avoid using `*` for origins when credentials are enabled.

## Authentication Analysis
- Token flow:
  1. User logs in via [backend/app/api/v1/auth.py](backend/app/api/v1/auth.py).
  2. Authentication service issues access and refresh tokens via [backend/app/application/services/authentication_service.py](backend/app/application/services/authentication_service.py) and [backend/app/application/services/jwt_service.py](backend/app/application/services/jwt_service.py).
  3. Protected routes depend on [backend/app/api/dependencies/auth.py](backend/app/api/dependencies/auth.py) and [backend/app/api/dependencies/permissions.py](backend/app/api/dependencies/permissions.py).
- Unauthorized error root causes:
  - `get_current_user` wraps failures into a 401 with `WWW-Authenticate: Bearer`.
  - The dependency catches any exception and turns it into the generic credential error, which can make debugging difficult.
  - `OAuth2PasswordBearer` is configured at `/api/v1/auth/token`, but the auth router also exposes `/login` and `/token` handlers; this creates some ambiguity for clients.
- JWT status: FAIL
  - The implementation is functional at a basic level, but fallback secrets and weak environment handling make it unsafe for production.

## Validation Analysis
- Pydantic usage is present throughout [backend/app/application/dtos](backend/app/application/dtos), and the shared base for camelCase serialization is in [backend/app/application/dtos/base.py](backend/app/application/dtos/base.py).
- Notable schema risks:
  - Some DTOs use plain `BaseModel` rather than the shared DTO base, which can lead to inconsistent serialization.
  - Several routes return raw dicts or manually serialized payloads while declaring a response model, which can cause unexpected 422/serialization issues during response validation.
  - The auth DTO layer is simpler than the rest and may not reflect the richer domain models used by services.
- Likely 422 risk endpoints:
  - Routes returning manual `JSONResponse` payloads rather than typed Pydantic models, especially in [backend/app/api/v1/invoices.py](backend/app/api/v1/invoices.py), [backend/app/api/v1/fuel_transactions.py](backend/app/api/v1/fuel_transactions.py), and [backend/app/api/v1/fuel_vendors.py](backend/app/api/v1/fuel_vendors.py).
- Validation status: FAIL

## Endpoint Inventory

| METHOD | PATH | AUTH REQUIRED | ROLE | REQUEST MODEL | RESPONSE MODEL |
| --- | --- | --- | --- | --- | --- |
| POST | /api/v1/auth/login | No | None | LoginRequest | LoginResponse |
| POST | /api/v1/auth/token | No | None | OAuth2PasswordRequestForm | dict |
| PUT | /api/v1/auth/change-password | Yes | None | ChangePasswordRequest | None |
| GET | /api/v1/users | Yes | users:read | None | APIResponse[PaginatedData[UserResponse]] |
| POST | /api/v1/users | Yes | users:create | UserCreate | APIResponse[UserResponse] |
| GET | /api/v1/users/{id} | Yes | users:read | None | APIResponse[UserResponse] |
| PUT | /api/v1/users/{id} | Yes | users:update | UserUpdate | APIResponse[UserResponse] |
| PATCH | /api/v1/users/{id} | Yes | users:update | UserUpdate | APIResponse[UserResponse] |
| DELETE | /api/v1/users/{id} | Yes | users:delete | None | APIResponse[None] |
| GET | /api/v1/roles | Yes | roles:read | None | APIResponse[list[RoleResponse]] |
| POST | /api/v1/roles | Yes | roles:create | RoleCreate | APIResponse[RoleResponse] |
| GET | /api/v1/drivers | Yes | drivers:read | None | APIResponse[PaginatedData[DriverResponse]] |
| GET | /api/v1/tractors | Yes | tractors:read | None | APIResponse[PaginatedData[TractorResponse]] |
| GET | /api/v1/trips | Yes | trips:read | None | APIResponse[PaginatedData[TripResponse]] |
| GET | /api/v1/invoices | Yes | trips:read | None | APIResponse[PaginatedData[InvoiceResponse]] |
| GET | /api/v1/reports | Yes | reports:dashboard | None | DashboardKPIResponse |
| GET | /api/v1/sessions | Yes | auth:read | None | list[SessionResponse] |
| DELETE | /api/v1/sessions | Yes | auth:update | None | dict |

## Recommended Fix Order
1. Startup issues
2. CORS
3. JWT authentication
4. Role authorization
5. Validation
6. Exception handling
7. Response consistency
8. Performance improvements

## Quick Wins
- Remove the duplicate auth router include in [backend/app/api/router.py](backend/app/api/router.py).
- Make the JWT secret mandatory instead of relying on a fallback.
- Replace the hardcoded admin default password with an environment-controlled bootstrap value.
- Add an explicit allowlist for the frontend origins in [backend/app/core/settings.py](backend/app/core/settings.py).
- Standardize all route responses around the shared envelope in [backend/app/schemas/response.py](backend/app/schemas/response.py).

## Final Verdict
- The backend is not ready for frontend integration as-is.
- Main blockers remain: startup/router stability, JWT secret handling, auth/authorization consistency, and response-model consistency.

## Terminal Summary
- Total endpoints: 121 route decorators detected across the router modules, but the runtime app registration was not reliably surfaced in the verification environment.
- Protected endpoints: Many endpoints rely on permission checks; the API is heavily protected.
- CORS status: FAIL
- JWT status: FAIL
- Validation status: FAIL
- Top 5 files requiring immediate attention:
  - [backend/app/core/security.py](backend/app/core/security.py)
  - [backend/app/core/settings.py](backend/app/core/settings.py)
  - [backend/app/main.py](backend/app/main.py)
  - [backend/app/api/router.py](backend/app/api/router.py)
  - [backend/app/api/dependencies/auth.py](backend/app/api/dependencies/auth.py)
