# Database Schema Design - Transport Tractor Management System (TTMS)

This document outlines the enterprise-grade database schema for the Transport Tractor Management System (TTMS). The design assumes PostgreSQL as the target RDBMS, using UUIDs for primary keys, strict foreign key constraints, indexes for performance optimization, and optimistic concurrency control (`version_id`).

---

## Global Base Schema (Audit Fields)

Every database table (except pure junction tables where audit fields are unnecessary) contains the following fields to satisfy domain auditing and soft delete requirements:

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | Unique identifier. |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT clock_timestamp()` | Creation timestamp. |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT clock_timestamp()` | Last modification timestamp. |
| `created_by` | `UUID` | `FOREIGN KEY REFERENCES users(id)`, `NULL` | User who created the record. |
| `updated_by` | `UUID` | `FOREIGN KEY REFERENCES users(id)`, `NULL` | User who last updated the record. |
| `deleted_at` | `TIMESTAMPTZ` | `NULL` | Soft delete timestamp. If non-null, the record is soft-deleted. |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT TRUE` | Active flag for logical filtering. |
| `version_id` | `INTEGER` | `NOT NULL`, `DEFAULT 1` | Optimistic concurrency control version number. |

---

## 1. Authentication & RBAC

### 1.1 `roles`
* **Purpose**: Defines system access authorization groups (e.g., Administrator, Dispatcher, Driver, Accountant).
* **Columns**:
  * Base audit columns
  * `name` (`VARCHAR(50)`, `NOT NULL`): Machine-readable name (e.g., `role_admin`).
  * `display_name` (`VARCHAR(100)`, `NOT NULL`): Human-readable name (e.g., "System Administrator").
  * `description` (`TEXT`, `NULL`)
* **Relationships**:
  * **One-to-Many**: `user_roles.role_id`, `role_permissions.role_id`
  * **Many-to-One**: None
  * **Many-to-Many**: `users` (via `user_roles`), `permissions` (via `role_permissions`)
* **Foreign Keys**: None
* **Constraints**:
  * `uq_roles_name`: `UNIQUE(name)` (Filtered by `deleted_at IS NULL` for soft delete compatibility)
* **Indexes**:
  * `idx_roles_name`: Unique B-Tree index on `name` where `deleted_at IS NULL`.
* **Unique Keys**: `name` (active only)

---

### 1.2 `permissions`
* **Purpose**: Fine-grained access privileges (e.g., `trips:create`, `invoices:approve`).
* **Columns**:
  * Base audit columns
  * `code` (`VARCHAR(100)`, `NOT NULL`): Permission code (e.g., `trips:create`).
  * `description` (`TEXT`, `NULL`)
* **Relationships**:
  * **One-to-Many**: `role_permissions.permission_id`
  * **Many-to-One**: None
  * **Many-to-Many**: `roles` (via `role_permissions`)
* **Foreign Keys**: None
* **Constraints**:
  * `uq_permissions_code`: `UNIQUE(code)`
* **Indexes**:
  * `idx_permissions_code`: Unique B-Tree index on `code` where `deleted_at IS NULL`.
* **Unique Keys**: `code` (active only)

---

### 1.3 `role_permissions`
* **Purpose**: Junction table connecting roles to their authorized permissions.
* **Columns**:
  * `role_id` (`UUID`, `NOT NULL`)
  * `permission_id` (`UUID`, `NOT NULL`)
  * `created_at` (`TIMESTAMPTZ`, `NOT NULL`, `DEFAULT clock_timestamp()`)
  * `created_by` (`UUID`, `NULL`)
* **Relationships**:
  * **Many-to-One**: `roles` (via `role_id`), `permissions` (via `permission_id`)
* **Foreign Keys**:
  * `fk_role_permissions_role_id`: `role_id REFERENCES roles(id) ON DELETE CASCADE`
  * `fk_role_permissions_permission_id`: `permission_id REFERENCES permissions(id) ON DELETE CASCADE`
* **Constraints**:
  * `pk_role_permissions`: `PRIMARY KEY (role_id, permission_id)`
* **Indexes**:
  * `idx_role_permissions_perm_id`: B-Tree index on `permission_id` (helps with reverse lookup).
* **Unique Keys**: `(role_id, permission_id)`

---

### 1.4 `users`
* **Purpose**: System users, credential validation, login capability.
* **Columns**:
  * Base audit columns
  * `email` (`VARCHAR(255)`, `NOT NULL`): Principal identifier.
  * `username` (`VARCHAR(100)`, `NOT NULL`): Optional alternate username.
  * `password_hash` (`VARCHAR(255)`, `NOT NULL`): Hashed credentials (e.g., bcrypt/argon2).
  * `first_name` (`VARCHAR(100)`, `NOT NULL`)
  * `last_name` (`VARCHAR(100)`, `NOT NULL`)
  * `phone` (`VARCHAR(30)`, `NULL`)
* **Relationships**:
  * **One-to-Many**: `user_roles.user_id`, `refresh_tokens.user_id`, `audit_logs.user_id`, `notifications.user_id`, `drivers.user_id` (nullable profile link)
  * **Many-to-One**: None
  * **Many-to-Many**: `roles` (via `user_roles`)
* **Foreign Keys**: None
* **Constraints**:
  * `uq_users_email`: `UNIQUE(email)`
  * `uq_users_username`: `UNIQUE(username)`
* **Indexes**:
  * `idx_users_email`: Unique B-Tree index on `email` where `deleted_at IS NULL`.
  * `idx_users_username`: Unique B-Tree index on `username` where `deleted_at IS NULL`.
* **Unique Keys**: `email`, `username` (active only)

---

### 1.5 `user_roles`
* **Purpose**: Junction table connecting users to their roles.
* **Columns**:
  * `user_id` (`UUID`, `NOT NULL`)
  * `role_id` (`UUID`, `NOT NULL`)
  * `created_at` (`TIMESTAMPTZ`, `NOT NULL`, `DEFAULT clock_timestamp()`)
  * `created_by` (`UUID`, `NULL`)
* **Relationships**:
  * **Many-to-One**: `users` (via `user_id`), `roles` (via `role_id`)
* **Foreign Keys**:
  * `fk_user_roles_user_id`: `user_id REFERENCES users(id) ON DELETE CASCADE`
  * `fk_user_roles_role_id`: `role_id REFERENCES roles(id) ON DELETE CASCADE`
* **Constraints**:
  * `pk_user_roles`: `PRIMARY KEY (user_id, role_id)`
* **Indexes**:
  * `idx_user_roles_role_id`: B-Tree index on `role_id`
* **Unique Keys**: `(user_id, role_id)`

---

### 1.6 `refresh_tokens`
* **Purpose**: Tracks issued JWT refresh tokens, enabling revocation and token rotation.
* **Columns**:
  * `id` (`UUID`, `PRIMARY KEY`, `DEFAULT gen_random_uuid()`)
  * `user_id` (`UUID`, `NOT NULL`)
  * `token` (`VARCHAR(512)`, `NOT NULL`): Secure random token hash or signature identifier.
  * `expires_at` (`TIMESTAMPTZ`, `NOT NULL`)
  * `issued_at` (`TIMESTAMPTZ`, `NOT NULL`, `DEFAULT clock_timestamp()`)
  * `revoked_at` (`TIMESTAMPTZ`, `NULL`)
  * `replaced_by_token` (`VARCHAR(512)`, `NULL`): Links to new token if rotated.
* **Relationships**:
  * **Many-to-One**: `users` (via `user_id`)
* **Foreign Keys**:
  * `fk_refresh_tokens_user_id`: `user_id REFERENCES users(id) ON DELETE CASCADE`
* **Constraints**:
  * `uq_refresh_tokens_token`: `UNIQUE(token)`
* **Indexes**:
  * `idx_refresh_tokens_token`: Unique index on `token`.
  * `idx_refresh_tokens_user_expiry`: B-Tree index on `(user_id, expires_at)`.
* **Unique Keys**: `token`

---

## 2. Fleet & Master Data

### 2.1 `drivers`
* **Purpose**: Maintains tractor drivers' details, licensing information, and payroll structures.
* **Columns**:
  * Base audit columns
  * `user_id` (`UUID`, `NULL`): Link to system user login profile (if driver has mobile/portal app access).
  * `employee_code` (`VARCHAR(50)`, `NOT NULL`): Unique business code for driver records.
  * `license_number` (`VARCHAR(50)`, `NOT NULL`)
  * `license_expiry` (`DATE`, `NOT NULL`)
  * `license_class` (`VARCHAR(30)`, `NOT NULL`)
  * `contact_phone` (`VARCHAR(30)`, `NOT NULL`)
  * `emergency_contact_phone` (`VARCHAR(30)`, `NULL`)
  * `fixed_salary` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`): Flat monthly salary if applicable.
  * `commission_percentage` (`NUMERIC(5, 2)`, `NOT NULL`, `DEFAULT 0.00`): Payout percentage per trip.
  * `driver_type` (`VARCHAR(20)`, `NOT NULL`): `SALARIED`, `COMMISSION_BASED`, `CONTRACT`.
  * `current_status` (`VARCHAR(20)`, `NOT NULL`, `DEFAULT 'AVAILABLE'`): `AVAILABLE`, `ON_TRIP`, `ON_LEAVE`, `INACTIVE`.
* **Relationships**:
  * **One-to-Many**: `trips.driver_id`, `fuel_logs.driver_id`, `driver_settlements.driver_id`, `driver_advances.driver_id`
  * **Many-to-One**: `users` (via `user_id`)
* **Foreign Keys**:
  * `fk_drivers_user_id`: `user_id REFERENCES users(id) ON DELETE SET NULL`
* **Constraints**:
  * `uq_drivers_employee_code`: `UNIQUE(employee_code)` where `deleted_at IS NULL`
  * `uq_drivers_license`: `UNIQUE(license_number)` where `deleted_at IS NULL`
  * `chk_drivers_salary`: `CHECK (fixed_salary >= 0)`
  * `chk_drivers_commission`: `CHECK (commission_percentage >= 0 AND commission_percentage <= 100)`
* **Indexes**:
  * `idx_drivers_license`: B-Tree index on `license_number`.
  * `idx_drivers_user_id`: B-Tree index on `user_id` where `user_id IS NOT NULL`.
  * `idx_drivers_status`: B-Tree index on `current_status` where `deleted_at IS NULL`.
* **Unique Keys**: `employee_code`, `license_number` (active only)

---

### 2.2 `driver_advances`
* **Purpose**: Tracks advances paid to drivers for fuel, tolls, meals, or cash advance during trips.
* **Columns**:
  * Base audit columns
  * `driver_id` (`UUID`, `NOT NULL`)
  * `amount` (`NUMERIC(12, 2)`, `NOT NULL`)
  * `advance_date` (`DATE`, `NOT NULL`)
  * `purpose` (`VARCHAR(255)`, `NULL`): e.g., "Trip Expense Advance", "Personal Loan".
  * `status` (`VARCHAR(20)`, `NOT NULL`, `DEFAULT 'PENDING'`): `PENDING`, `SETTLED`, `WAIVED`.
  * `settled_at` (`TIMESTAMPTZ`, `NULL`)
* **Relationships**:
  * **Many-to-One**: `drivers` (via `driver_id`)
* **Foreign Keys**:
  * `fk_driver_advances_driver_id`: `driver_id REFERENCES drivers(id) ON DELETE RESTRICT`
* **Constraints**:
  * `chk_driver_advances_amount`: `CHECK (amount > 0)`
* **Indexes**:
  * `idx_driver_advances_status`: B-Tree index on `(driver_id, status)`.
* **Unique Keys**: None

---

### 2.3 `tractors`
* **Purpose**: Represents heavy vehicle assets, tracking licensing, maintenance metrics, and specs.
* **Columns**:
  * Base audit columns
  * `registration_number` (`VARCHAR(30)`, `NOT NULL`): e.g., license plate.
  * `chassis_number` (`VARCHAR(100)`, `NOT NULL`)
  * `engine_number` (`VARCHAR(100)`, `NOT NULL`)
  * `make` (`VARCHAR(50)`, `NOT NULL`)
  * `model` (`VARCHAR(50)`, `NOT NULL`)
  * `year_manufactured` (`INTEGER`, `NOT NULL`)
  * `ownership_type` (`VARCHAR(20)`, `NOT NULL`): `OWNED`, `LEASED`, `MARKET_HIRE`.
  * `insurance_expiry` (`DATE`, `NOT NULL`)
  * `fitness_certificate_expiry` (`DATE`, `NOT NULL`)
  * `road_tax_expiry` (`DATE`, `NOT NULL`)
  * `current_odometer` (`NUMERIC(10, 2)`, `NOT NULL`, `DEFAULT 0.00`)
  * `status` (`VARCHAR(20)`, `NOT NULL`, `DEFAULT 'ACTIVE'`): `ACTIVE`, `IN_MAINTENANCE`, `OUT_OF_SERVICE`.
* **Relationships**:
  * **One-to-Many**: `trips.tractor_id`, `fuel_logs.tractor_id`, `tractor_maintenance_logs.tractor_id`, `expenses.tractor_id`
* **Foreign Keys**: None
* **Constraints**:
  * `uq_tractors_registration`: `UNIQUE(registration_number)` where `deleted_at IS NULL`
  * `chk_tractors_odometer`: `CHECK (current_odometer >= 0)`
* **Indexes**:
  * `idx_tractors_registration`: Unique B-Tree index on `registration_number` where `deleted_at IS NULL`.
  * `idx_tractors_expiries`: B-Tree index on `(insurance_expiry, fitness_certificate_expiry, road_tax_expiry)`.
* **Unique Keys**: `registration_number` (active only)

---

### 2.4 `tractor_maintenance_logs`
* **Purpose**: Tracks repairs, preventative maintenance, parts replaced, and downtime costs.
* **Columns**:
  * Base audit columns
  * `tractor_id` (`UUID`, `NOT NULL`)
  * `maintenance_date` (`DATE`, `NOT NULL`)
  * `description` (`TEXT`, `NOT NULL`): e.g., "Engine oil change, filter replacement".
  * `odometer_reading` (`NUMERIC(10, 2)`, `NOT NULL`)
  * `cost` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`)
  * `vendor_name` (`VARCHAR(150)`, `NULL`): Workshop or mechanic shop name.
  * `performed_by` (`VARCHAR(100)`, `NULL`)
  * `maintenance_type` (`VARCHAR(20)`, `NOT NULL`): `ROUTINE`, `REPAIR`, `BREAKDOWN`, `TYRE_CHANGE`.
* **Relationships**:
  * **Many-to-One**: `tractors` (via `tractor_id`)
* **Foreign Keys**:
  * `fk_tractor_maintenance_tractor_id`: `tractor_id REFERENCES tractors(id) ON DELETE RESTRICT`
* **Constraints**:
  * `chk_maintenance_cost`: `CHECK (cost >= 0)`
  * `chk_maintenance_odometer`: `CHECK (odometer_reading >= 0)`
* **Indexes**:
  * `idx_tractor_maintenance_date`: B-Tree index on `(tractor_id, maintenance_date DESC)`.
* **Unique Keys**: None

---

### 2.5 `parties`
* **Purpose**: Clients/Billing Entities who book trips, pay invoices, or act as external transport contractors.
* **Columns**:
  * Base audit columns
  * `code` (`VARCHAR(50)`, `NOT NULL`): Short code for UI selection (e.g., `PART_SHREE`).
  * `name` (`VARCHAR(150)`, `NOT NULL`): Registered company name.
  * `tax_identifier` (`VARCHAR(50)`, `NULL`): e.g., GSTIN/EIN/VAT.
  * `billing_address` (`TEXT`, `NOT NULL`)
  * `contact_person` (`VARCHAR(100)`, `NOT NULL`)
  * `contact_phone` (`VARCHAR(30)`, `NOT NULL`)
  * `contact_email` (`VARCHAR(255)`, `NULL`)
  * `outstanding_balance` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`): Running customer balance.
  * `payment_terms_days` (`INTEGER`, `NOT NULL`, `DEFAULT 30`)
  * `party_type` (`VARCHAR(20)`, `NOT NULL`): `CUSTOMER`, `SUPPLIER`, `INTERNAL`.
* **Relationships**:
  * **One-to-Many**: `trips.party_id`, `invoices.party_id`, `payments.party_id`, `party_rates.party_id`
* **Foreign Keys**: None
* **Constraints**:
  * `uq_parties_code`: `UNIQUE(code)` where `deleted_at IS NULL`
  * `uq_parties_tax_id`: `UNIQUE(tax_identifier)` where `tax_identifier IS NOT NULL AND deleted_at IS NULL`
  * `chk_parties_outstanding`: `CHECK (outstanding_balance IS NOT NULL)`
* **Indexes**:
  * `idx_parties_code`: Unique index on `code`.
  * `idx_parties_name`: B-Tree index for name prefix matching (GIN/Trigram or standard B-Tree).
* **Unique Keys**: `code`, `tax_identifier` (active only)

---

### 2.6 `quarries`
* **Purpose**: Represents quarries, mine sites, or load terminals from which tractors transport materials.
* **Columns**:
  * Base audit columns
  * `name` (`VARCHAR(150)`, `NOT NULL`)
  * `location` (`TEXT`, `NOT NULL`): Address, GPS coordinates, or area code.
  * `contact_phone` (`VARCHAR(30)`, `NULL`)
  * `permit_number` (`VARCHAR(100)`, `NULL`): Operational quarry licenses.
  * `is_third_party` (`BOOLEAN`, `NOT NULL`, `DEFAULT TRUE`)
* **Relationships**:
  * **One-to-Many**: `trips.quarry_id`, `party_rates.quarry_id`
* **Foreign Keys**: None
* **Constraints**:
  * `uq_quarries_name`: `UNIQUE(name)` where `deleted_at IS NULL`
* **Indexes**:
  * `idx_quarries_name`: Unique B-Tree index on `name` where `deleted_at IS NULL`.
* **Unique Keys**: `name` (active only)

---

### 2.7 `materials`
* **Purpose**: Categories of materials hauled (e.g., M-Sand, River Sand, Blue Metal 20mm, Aggregate, Stone Dust).
* **Columns**:
  * Base audit columns
  * `name` (`VARCHAR(100)`, `NOT NULL`)
  * `unit_of_measure` (`VARCHAR(20)`, `NOT NULL`, `DEFAULT 'TONS'`): e.g., `TONS`, `BRASS`, `TRIP`.
  * `density_factor` (`NUMERIC(6, 3)`, `NULL`): Conversion ratio for weight-to-volume calculations.
* **Relationships**:
  * **One-to-Many**: `trips.material_id`, `party_rates.material_id`
* **Foreign Keys**: None
* **Constraints**:
  * `uq_materials_name`: `UNIQUE(name)` where `deleted_at IS NULL`
* **Indexes**:
  * `idx_materials_name`: Unique B-Tree index on `name` where `deleted_at IS NULL`.
* **Unique Keys**: `name` (active only)

---

### 2.8 `party_rates`
* **Purpose**: Master contract rates. Automatically maps pricing for a specific customer, quarry location, and material.
* **Columns**:
  * Base audit columns
  * `party_id` (`UUID`, `NOT NULL`)
  * `quarry_id` (`UUID`, `NOT NULL`)
  * `material_id` (`UUID`, `NOT NULL`)
  * `rate_per_unit` (`NUMERIC(10, 2)`, `NOT NULL`)
  * `driver_commission_rate` (`NUMERIC(10, 2)`, `NOT NULL`, `DEFAULT 0.00`): Optional commission override rate for driver on this route.
  * `effective_from` (`DATE`, `NOT NULL`)
  * `effective_to` (`DATE`, `NULL`): Standard date range validity mapping.
* **Relationships**:
  * **Many-to-One**: `parties` (via `party_id`), `quarries` (via `quarry_id`), `materials` (via `material_id`)
* **Foreign Keys**:
  * `fk_party_rates_party`: `party_id REFERENCES parties(id) ON DELETE RESTRICT`
  * `fk_party_rates_quarry`: `quarry_id REFERENCES quarries(id) ON DELETE RESTRICT`
  * `fk_party_rates_material`: `material_id REFERENCES materials(id) ON DELETE RESTRICT`
* **Constraints**:
  * `chk_party_rates_price`: `CHECK (rate_per_unit >= 0)`
  * `chk_party_rates_dates`: `CHECK (effective_to IS NULL OR effective_to >= effective_from)`
* **Indexes**:
  * `idx_party_rates_lookup`: B-Tree index on `(party_id, quarry_id, material_id, effective_from, effective_to)`.
* **Unique Keys**: `(party_id, quarry_id, material_id, effective_from)` (prevents concurrent double mappings).

---

## 3. Operations

### 3.1 `trips`
* **Purpose**: The main core transactional table tracking a single trip made by a tractor.
* **Columns**:
  * Base audit columns
  * `trip_number` (`VARCHAR(50)`, `NOT NULL`): Formatted sequence reference (e.g., `TRIP-202607-0042`).
  * `trip_date` (`DATE`, `NOT NULL`)
  * `tractor_id` (`UUID`, `NOT NULL`)
  * `driver_id` (`UUID`, `NOT NULL`)
  * `party_id` (`UUID`, `NOT NULL`)
  * `quarry_id` (`UUID`, `NOT NULL`)
  * `material_id` (`UUID`, `NOT NULL`)
  * `challan_number` (`VARCHAR(100)`, `NULL`): Paper loading slip/permit ID.
  * `challan_date` (`DATE`, `NULL`)
  * `gross_weight` (`NUMERIC(10, 2)`, `NULL`): Loaded weight in Metric Tons.
  * `tare_weight` (`NUMERIC(10, 2)`, `NULL`): Empty tractor weight.
  * `net_weight` (`NUMERIC(10, 2)`, `NOT NULL`): Weight of material billed (`gross_weight - tare_weight`).
  * `unit_rate` (`NUMERIC(10, 2)`, `NOT NULL`): Customer rate per Ton or Unit.
  * `trip_amount` (`NUMERIC(12, 2)`, `NOT NULL`): Calculated gross billing (`net_weight * unit_rate`).
  * `driver_commission_amount` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`): Computed driver commission.
  * `status` (`VARCHAR(20)`, `NOT NULL`, `DEFAULT 'PENDING'`): `PENDING`, `DISPATCHED`, `COMPLETED`, `INVOICED`, `CANCELLED`.
  * `remarks` (`TEXT`, `NULL`)
  * `invoice_item_id` (`UUID`, `NULL`): Reference to invoice line item (once billed).
* **Relationships**:
  * **Many-to-One**: `tractors` (via `tractor_id`), `drivers` (via `driver_id`), `parties` (via `party_id`), `quarries` (via `quarry_id`), `materials` (via `material_id`), `invoice_items` (via `invoice_item_id`)
  * **One-to-Many**: `expenses.trip_id`, `fuel_logs.trip_id`
* **Foreign Keys**:
  * `fk_trips_tractor`: `tractor_id REFERENCES tractors(id) ON DELETE RESTRICT`
  * `fk_trips_driver`: `driver_id REFERENCES drivers(id) ON DELETE RESTRICT`
  * `fk_trips_party`: `party_id REFERENCES parties(id) ON DELETE RESTRICT`
  * `fk_trips_quarry`: `quarry_id REFERENCES quarries(id) ON DELETE RESTRICT`
  * `fk_trips_material`: `material_id REFERENCES materials(id) ON DELETE RESTRICT`
  * `fk_trips_invoice_item`: `invoice_item_id REFERENCES invoice_items(id) ON DELETE SET NULL`
* **Constraints**:
  * `uq_trips_trip_number`: `UNIQUE(trip_number)`
  * `chk_trips_net_weight`: `CHECK (net_weight >= 0)`
  * `chk_trips_gross_tare`: `CHECK (gross_weight >= tare_weight)`
  * `chk_trips_unit_rate`: `CHECK (unit_rate >= 0)`
  * `chk_trips_amount`: `CHECK (trip_amount >= 0)`
* **Indexes**:
  * `idx_trips_trip_number`: Unique index on `trip_number` where `deleted_at IS NULL`.
  * `idx_trips_composite_lookup`: B-Tree index on `(party_id, trip_date DESC, status)`.
  * `idx_trips_tractor_date`: B-Tree index on `(tractor_id, trip_date DESC)`.
  * `idx_trips_driver_date`: B-Tree index on `(driver_id, trip_date DESC)`.
  * `idx_trips_invoice_item`: B-Tree index on `invoice_item_id` where `invoice_item_id IS NOT NULL`.
* **Unique Keys**: `trip_number`

---

### 3.2 `fuel_logs`
* **Purpose**: Details tractor diesel intake, calculating consumption efficiency (km/l or ton/km).
* **Columns**:
  * Base audit columns
  * `tractor_id` (`UUID`, `NOT NULL`)
  * `driver_id` (`UUID`, `NOT NULL`)
  * `trip_id` (`UUID`, `NULL`): Optional link if fuel was taken during/specifically for a trip.
  * `fill_date` (`DATE`, `NOT NULL`)
  * `odometer_reading` (`NUMERIC(10, 2)`, `NOT NULL`)
  * `liters` (`NUMERIC(8, 2)`, `NOT NULL`)
  * `price_per_liter` (`NUMERIC(8, 2)`, `NOT NULL`)
  * `total_cost` (`NUMERIC(12, 2)`, `NOT NULL`): `liters * price_per_liter`
  * `fuel_station` (`VARCHAR(150)`, `NOT NULL`)
  * `receipt_number` (`VARCHAR(100)`, `NULL`)
* **Relationships**:
  * **Many-to-One**: `tractors` (via `tractor_id`), `drivers` (via `driver_id`), `trips` (via `trip_id`)
* **Foreign Keys**:
  * `fk_fuel_logs_tractor`: `tractor_id REFERENCES tractors(id) ON DELETE RESTRICT`
  * `fk_fuel_logs_driver`: `driver_id REFERENCES drivers(id) ON DELETE RESTRICT`
  * `fk_fuel_logs_trip`: `trip_id REFERENCES trips(id) ON DELETE SET NULL`
* **Constraints**:
  * `chk_fuel_liters`: `CHECK (liters > 0)`
  * `chk_fuel_price`: `CHECK (price_per_liter > 0)`
  * `chk_fuel_odometer`: `CHECK (odometer_reading >= 0)`
  * `chk_fuel_cost`: `CHECK (total_cost >= 0)`
* **Indexes**:
  * `idx_fuel_logs_tractor_date`: B-Tree index on `(tractor_id, fill_date DESC)`.
  * `idx_fuel_logs_trip`: B-Tree index on `trip_id` where `trip_id IS NOT NULL`.
* **Unique Keys**: None

---

## 4. Finance, Invoicing & Payments

### 4.1 `expense_categories`
* **Purpose**: Custom lookup category configurations for bookkeeping (e.g., Diesel, Tolls, Police/RTO bribe, Spares, Driver Food).
* **Columns**:
  * Base audit columns
  * `name` (`VARCHAR(100)`, `NOT NULL`)
  * `description` (`TEXT`, `NULL`)
* **Relationships**:
  * **One-to-Many**: `expenses.category_id`
* **Foreign Keys**: None
* **Constraints**:
  * `uq_expense_cat_name`: `UNIQUE(name)` where `deleted_at IS NULL`
* **Indexes**:
  * `idx_expense_cat_name`: Unique B-Tree index on `name` where `deleted_at IS NULL`.
* **Unique Keys**: `name` (active only)

---

### 4.2 `expenses`
* **Purpose**: General operational expenses, tractor repairs, or trip allowances.
* **Columns**:
  * Base audit columns
  * `category_id` (`UUID`, `NOT NULL`)
  * `tractor_id` (`UUID`, `NULL`): Link if expense is mapped to a specific tractor asset.
  * `trip_id` (`UUID`, `NULL`): Link if expense belongs directly to a single trip transaction.
  * `amount` (`NUMERIC(12, 2)`, `NOT NULL`)
  * `expense_date` (`DATE`, `NOT NULL`)
  * `recipient` (`VARCHAR(150)`, `NULL`): Entity/Person paid.
  * `notes` (`TEXT`, `NULL`)
  * `receipt_url` (`VARCHAR(512)`, `NULL`): Document path.
* **Relationships**:
  * **Many-to-One**: `expense_categories` (via `category_id`), `tractors` (via `tractor_id`), `trips` (via `trip_id`)
* **Foreign Keys**:
  * `fk_expenses_category`: `category_id REFERENCES expense_categories(id) ON DELETE RESTRICT`
  * `fk_expenses_tractor`: `tractor_id REFERENCES tractors(id) ON DELETE SET NULL`
  * `fk_expenses_trip`: `trip_id REFERENCES trips(id) ON DELETE CASCADE`
* **Constraints**:
  * `chk_expenses_amount`: `CHECK (amount > 0)`
* **Indexes**:
  * `idx_expenses_trip`: B-Tree index on `trip_id` where `trip_id IS NOT NULL`.
  * `idx_expenses_tractor`: B-Tree index on `tractor_id` where `tractor_id IS NOT NULL`.
  * `idx_expenses_date`: B-Tree index on `expense_date DESC`.
* **Unique Keys**: None

---

### 4.3 `invoices`
* **Purpose**: Formal billing invoices issued to client parties aggregating trips.
* **Columns**:
  * Base audit columns
  * `invoice_number` (`VARCHAR(50)`, `NOT NULL`): Formatted sequence reference (e.g., `INV-202607-0012`).
  * `party_id` (`UUID`, `NOT NULL`): Customer client.
  * `issue_date` (`DATE`, `NOT NULL`)
  * `due_date` (`DATE`, `NOT NULL`)
  * `sub_total` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`): Cost of trips.
  * `tax_amount` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`)
  * `discount_amount` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`)
  * `total_amount` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`): Calculated final invoice.
  * `paid_amount` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`)
  * `status` (`VARCHAR(20)`, `NOT NULL`, `DEFAULT 'DRAFT'`): `DRAFT`, `SENT`, `PAID`, `PARTIALLY_PAID`, `OVERDUE`, `VOID`.
  * `pdf_url` (`VARCHAR(512)`, `NULL`): Generated storage path.
* **Relationships**:
  * **Many-to-One**: `parties` (via `party_id`)
  * **One-to-Many**: `invoice_items.invoice_id`, `payments.invoice_id`
* **Foreign Keys**:
  * `fk_invoices_party`: `party_id REFERENCES parties(id) ON DELETE RESTRICT`
* **Constraints**:
  * `uq_invoices_number`: `UNIQUE(invoice_number)`
  * `chk_invoices_dates`: `CHECK (due_date >= issue_date)`
  * `chk_invoices_amounts`: `CHECK (total_amount >= 0 AND sub_total >= 0 AND tax_amount >= 0 AND discount_amount >= 0)`
  * `chk_invoices_paid`: `CHECK (paid_amount <= total_amount AND paid_amount >= 0)`
* **Indexes**:
  * `idx_invoices_number`: Unique index on `invoice_number` where `deleted_at IS NULL`.
  * `idx_invoices_party_status`: B-Tree index on `(party_id, status)`.
  * `idx_invoices_due`: B-Tree index on `due_date DESC`.
* **Unique Keys**: `invoice_number`

---

### 4.4 `invoice_items`
* **Purpose**: Line items detailing the composition of an invoice (usually maps to one Trip).
* **Columns**:
  * `id` (`UUID`, `PRIMARY KEY`, `DEFAULT gen_random_uuid()`)
  * `invoice_id` (`UUID`, `NOT NULL`)
  * `trip_id` (`UUID`, `NOT NULL`): Trip linked to this invoice line item.
  * `description` (`VARCHAR(255)`, `NOT NULL`)
  * `amount` (`NUMERIC(12, 2)`, `NOT NULL`)
  * `created_at` (`TIMESTAMPTZ`, `NOT NULL`, `DEFAULT clock_timestamp()`)
* **Relationships**:
  * **Many-to-One**: `invoices` (via `invoice_id`), `trips` (via `trip_id`)
* **Foreign Keys**:
  * `fk_invoice_items_invoice`: `invoice_id REFERENCES invoices(id) ON DELETE CASCADE`
  * `fk_invoice_items_trip`: `trip_id REFERENCES trips(id) ON DELETE RESTRICT`
* **Constraints**:
  * `uq_invoice_items_trip`: `UNIQUE(trip_id)` (prevents single trip from being invoiced twice)
* **Indexes**:
  * `idx_invoice_items_invoice`: B-Tree index on `invoice_id`.
  * `idx_invoice_items_trip`: Unique index on `trip_id`.
* **Unique Keys**: `trip_id`

---

### 4.5 `driver_settlements`
* **Purpose**: Periodical payouts/settlements generated for drivers based on completed trips & salary.
* **Columns**:
  * Base audit columns
  * `driver_id` (`UUID`, `NOT NULL`)
  * `settlement_number` (`VARCHAR(50)`, `NOT NULL`): Formatted invoice code.
  * `start_date` (`DATE`, `NOT NULL`): Payroll cycle start.
  * `end_date` (`DATE`, `NOT NULL`): Payroll cycle end.
  * `gross_earnings` (`NUMERIC(12, 2)`, `NOT NULL`): Calculated commission + fixed base salary.
  * `advances_deducted` (`NUMERIC(12, 2)`, `NOT NULL`, `DEFAULT 0.00`): Taken from `driver_advances`.
  * `net_payable` (`NUMERIC(12, 2)`, `NOT NULL`): `gross_earnings - advances_deducted`.
  * `status` (`VARCHAR(20)`, `NOT NULL`, `DEFAULT 'PENDING'`): `PENDING`, `APPROVED`, `PAID`, `CANCELLED`.
  * `payout_date` (`DATE`, `NULL`)
* **Relationships**:
  * **Many-to-One**: `drivers` (via `driver_id`)
  * **One-to-Many**: `payments.driver_settlement_id`
* **Foreign Keys**:
  * `fk_driver_settlements_driver`: `driver_id REFERENCES drivers(id) ON DELETE RESTRICT`
  * `fk_driver_settlements_num`: `settlement_number REFERENCES driver_settlements(settlement_number)`
* **Constraints**:
  * `uq_driver_settlement_num`: `UNIQUE(settlement_number)`
  * `chk_settlement_dates`: `CHECK (end_date >= start_date)`
  * `chk_settlement_amounts`: `CHECK (net_payable = gross_earnings - advances_deducted)`
* **Indexes**:
  * `idx_driver_settlements_num`: Unique index on `settlement_number` where `deleted_at IS NULL`.
  * `idx_driver_settlements_driver`: B-Tree index on `(driver_id, status)`.
* **Unique Keys**: `settlement_number`

---

### 4.6 `payments`
* **Purpose**: Tracks money inflow (customer invoice collections) and outflow (driver payouts, fuel vendors).
* **Columns**:
  * Base audit columns
  * `payment_number` (`VARCHAR(50)`, `NOT NULL`): Formatted voucher reference code.
  * `party_id` (`UUID`, `NULL`): Link if client receipt or subcontractor payout.
  * `driver_id` (`UUID`, `NULL`): Link if driver salary payout.
  * `invoice_id` (`UUID`, `NULL`): Reference to customer invoice (for receipts).
  * `driver_settlement_id` (`UUID`, `NULL`): Reference to driver settlement voucher.
  * `payment_type` (`VARCHAR(20)`, `NOT NULL`): `RECEIPT` (money in), `DISBURSEMENT` (money out).
  * `amount` (`NUMERIC(12, 2)`, `NOT NULL`)
  * `payment_date` (`DATE`, `NOT NULL`)
  * `payment_method` (`VARCHAR(30)`, `NOT NULL`): `CASH`, `BANK_TRANSFER`, `UPI`, `CHEQUE`, `CREDIT_CARD`.
  * `reference_number` (`VARCHAR(100)`, `NULL`): Bank transaction ID or Cheque number.
  * `notes` (`TEXT`, `NULL`)
* **Relationships**:
  * **Many-to-One**: `parties` (via `party_id`), `drivers` (via `driver_id`), `invoices` (via `invoice_id`), `driver_settlements` (via `driver_settlement_id`)
* **Foreign Keys**:
  * `fk_payments_party`: `party_id REFERENCES parties(id) ON DELETE RESTRICT`
  * `fk_payments_driver`: `driver_id REFERENCES drivers(id) ON DELETE RESTRICT`
  * `fk_payments_invoice`: `invoice_id REFERENCES invoices(id) ON DELETE SET NULL`
  * `fk_payments_driver_settlement`: `driver_settlement_id REFERENCES driver_settlements(id) ON DELETE SET NULL`
* **Constraints**:
  * `uq_payments_number`: `UNIQUE(payment_number)`
  * `chk_payments_amount`: `CHECK (amount > 0)`
  * `chk_payments_target`: `CHECK ((party_id IS NOT NULL) OR (driver_id IS NOT NULL))` (Must link to a party or driver)
* **Indexes**:
  * `idx_payments_number`: Unique B-Tree index on `payment_number` where `deleted_at IS NULL`.
  * `idx_payments_invoice`: B-Tree index on `invoice_id` where `invoice_id IS NOT NULL`.
  * `idx_payments_settlement`: B-Tree index on `driver_settlement_id` where `driver_settlement_id IS NOT NULL`.
  * `idx_payments_party_date`: B-Tree index on `(party_id, payment_date DESC)`.
  * `idx_payments_driver_date`: B-Tree index on `(driver_id, payment_date DESC)`.
* **Unique Keys**: `payment_number`

---

## 5. System, Audit & Configurations

### 5.1 `audit_logs`
* **Purpose**: Keeps trace logs of mutations (CUD operations) across database entities.
* **Columns**:
  * `id` (`UUID`, `PRIMARY KEY`, `DEFAULT gen_random_uuid()`)
  * `user_id` (`UUID`, `NULL`): User performing the modification (if authenticated).
  * `action` (`VARCHAR(10)`, `NOT NULL`): `INSERT`, `UPDATE`, `DELETE`, `RESTORE`.
  * `table_name` (`VARCHAR(100)`, `NOT NULL`)
  * `record_id` (`UUID`, `NOT NULL`): Target entity PK ID.
  * `old_values` (`JSONB`, `NULL`): Record state before update/delete.
  * `new_values` (`JSONB`, `NULL`): Inserted values or update differences.
  * `ip_address` (`VARCHAR(45)`, `NULL`): IPv4 or IPv6 client source.
  * `user_agent` (`VARCHAR(512)`, `NULL`)
  * `created_at` (`TIMESTAMPTZ`, `NOT NULL`, `DEFAULT clock_timestamp()`)
* **Relationships**:
  * **Many-to-One**: `users` (via `user_id`)
* **Foreign Keys**:
  * `fk_audit_logs_user`: `user_id REFERENCES users(id) ON DELETE SET NULL`
* **Constraints**: None
* **Indexes**:
  * `idx_audit_logs_created_at`: B-Tree index on `created_at DESC` (essential for timestamp sorting).
  * `idx_audit_logs_target`: B-Tree index on `(table_name, record_id)`.
* **Unique Keys**: None

---

### 5.2 `notifications`
* **Purpose**: Holds system-generated alert warnings (such as license/insurance expiry warnings, overdue invoice notices).
* **Columns**:
  * Base audit columns
  * `user_id` (`UUID`, `NOT NULL`): Recipient user.
  * `title` (`VARCHAR(200)`, `NOT NULL`)
  * `message` (`TEXT`, `NOT NULL`)
  * `type` (`VARCHAR(30)`, `NOT NULL`): `ALERT`, `SYSTEM`, `INFO`, `EXPIRY_WARNING`.
  * `read_at` (`TIMESTAMPTZ`, `NULL`): Unread if `NULL`.
* **Relationships**:
  * **Many-to-One**: `users` (via `user_id`)
* **Foreign Keys**:
  * `fk_notifications_user`: `user_id REFERENCES users(id) ON DELETE CASCADE`
* **Indexes**:
  * `idx_notifications_user_unread`: B-Tree index on `(user_id, read_at)` where `read_at IS NULL`.
  * `idx_notifications_user_id`: B-Tree index on `user_id` where `deleted_at IS NULL`.
* **Unique Keys**: None

---

### 5.3 `settings`
* **Purpose**: Key-Value app config configurations (e.g. system tax rates, SMS/Email provider parameters).
* **Columns**:
  * Base audit columns
  * `key` (`VARCHAR(100)`, `NOT NULL`)
  * `value` (`TEXT`, `NOT NULL`): Serialized configuration.
  * `description` (`TEXT`, `NULL`)
* **Relationships**: None
* **Foreign Keys**: None
* **Constraints**:
  * `uq_settings_key`: `UNIQUE(key)` where `deleted_at IS NULL`
* **Indexes**:
  * `idx_settings_key`: Unique index on `key` where `deleted_at IS NULL`.
* **Unique Keys**: `key` (active only)
