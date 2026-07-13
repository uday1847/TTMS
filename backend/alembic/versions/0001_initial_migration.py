"""initial migration

Revision ID: 0001
Revises: 
Create Date: 2026-07-10 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create PostgreSQL native enum types
    op.execute("CREATE TYPE driver_status_enum AS ENUM ('available', 'on_trip', 'on_leave', 'inactive')")
    op.execute("CREATE TYPE tractor_status_enum AS ENUM ('active', 'in_maintenance', 'out_of_service')")
    op.execute("CREATE TYPE payment_type_enum AS ENUM ('receipt', 'disbursement')")
    op.execute("CREATE TYPE payment_mode_enum AS ENUM ('cash', 'bank_transfer', 'upi', 'cheque', 'credit_card')")
    op.execute("CREATE TYPE notification_type_enum AS ENUM ('alert', 'system', 'info', 'expiry_reminder', 'payment_reminder')")

    # 2. Create 'users' table first (core target for auditing relationships)
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=True),
        # Audit Fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    # Partial unique indexes for soft-deletes compatibility
    op.create_index('uq_users_email', 'users', ['email'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_users_username', 'users', ['username'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 3. Create independent tables
    # 'roles'
    op.create_table(
        'roles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_roles_name', 'roles', ['name'], unique=False)
    op.create_index('uq_roles_name', 'roles', ['name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'permissions'
    op.create_table(
        'permissions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_permissions_code', 'permissions', ['code'], unique=False)
    op.create_index('uq_permissions_code', 'permissions', ['code'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'settings'
    op.create_table(
        'settings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_settings_key', 'settings', ['key'], unique=False)
    op.create_index('uq_settings_key', 'settings', ['key'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'tractors'
    op.create_table(
        'tractors',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('registration_number', sa.String(length=30), nullable=False),
        sa.Column('chassis_number', sa.String(length=100), nullable=False),
        sa.Column('engine_number', sa.String(length=100), nullable=False),
        sa.Column('make', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('year_manufactured', sa.Integer(), nullable=False),
        sa.Column('ownership_type', sa.String(length=20), nullable=False),
        sa.Column('insurance_expiry', sa.Date(), nullable=False),
        sa.Column('fitness_certificate_expiry', sa.Date(), nullable=False),
        sa.Column('road_tax_expiry', sa.Date(), nullable=False),
        sa.Column('current_odometer', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'in_maintenance', 'out_of_service', name='tractor_status_enum', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('current_odometer >= 0', name='chk_tractors_odometer'),
    )
    op.create_index('ix_tractors_registration_number', 'tractors', ['registration_number'], unique=False)
    op.create_index('uq_tractors_registration_number', 'tractors', ['registration_number'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'parties'
    op.create_table(
        'parties',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('tax_identifier', sa.String(length=50), nullable=True),
        sa.Column('billing_address', sa.Text(), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=False),
        sa.Column('contact_phone', sa.String(length=30), nullable=False),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('outstanding_balance', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False),
        sa.Column('party_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_parties_code', 'parties', ['code'], unique=False)
    op.create_index('ix_parties_name', 'parties', ['name'], unique=False)
    op.create_index('ix_parties_tax_identifier', 'parties', ['tax_identifier'], unique=False)
    op.create_index('uq_parties_code', 'parties', ['code'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_parties_tax_identifier', 'parties', ['tax_identifier'], unique=True, postgresql_where=sa.text('tax_identifier IS NOT NULL AND deleted_at IS NULL'))

    # 'quarries'
    op.create_table(
        'quarries',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('location', sa.Text(), nullable=False),
        sa.Column('contact_phone', sa.String(length=30), nullable=True),
        sa.Column('permit_number', sa.String(length=100), nullable=True),
        sa.Column('is_third_party', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_quarries_name', 'quarries', ['name'], unique=False)
    op.create_index('uq_quarries_name', 'quarries', ['name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'materials'
    op.create_table(
        'materials',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=False),
        sa.Column('density_factor', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_materials_name', 'materials', ['name'], unique=False)
    op.create_index('uq_materials_name', 'materials', ['name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'expense_categories'
    op.create_table(
        'expense_categories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_expense_categories_name', 'expense_categories', ['name'], unique=False)
    op.create_index('uq_expense_categories_name', 'expense_categories', ['name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 4. Create junction / dependent tables
    # 'role_permissions'
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Uuid(), nullable=False),
        sa.Column('permission_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )

    # 'user_roles'
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('role_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )

    # 'refresh_tokens'
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('token', sa.String(length=512), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replaced_by_token', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=False)

    # 'drivers'
    op.create_table(
        'drivers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('employee_code', sa.String(length=50), nullable=False),
        sa.Column('license_number', sa.String(length=50), nullable=False),
        sa.Column('license_expiry', sa.Date(), nullable=False),
        sa.Column('license_class', sa.String(length=30), nullable=False),
        sa.Column('contact_phone', sa.String(length=30), nullable=False),
        sa.Column('emergency_contact_phone', sa.String(length=30), nullable=True),
        sa.Column('fixed_salary', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('commission_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('driver_type', sa.String(length=20), nullable=False),
        sa.Column('current_status', postgresql.ENUM('available', 'on_trip', 'on_leave', 'inactive', name='driver_status_enum', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('fixed_salary >= 0', name='chk_drivers_salary'),
        sa.CheckConstraint('commission_percentage >= 0 AND commission_percentage <= 100', name='chk_drivers_commission'),
    )
    op.create_index('ix_drivers_employee_code', 'drivers', ['employee_code'], unique=False)
    op.create_index('ix_drivers_license_number', 'drivers', ['license_number'], unique=False)
    op.create_index('uq_drivers_employee_code', 'drivers', ['employee_code'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_drivers_license_number', 'drivers', ['license_number'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'trips'
    op.create_table(
        'trips',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('trip_number', sa.String(length=50), nullable=False),
        sa.Column('trip_date', sa.Date(), nullable=False),
        sa.Column('tractor_id', sa.Uuid(), nullable=False),
        sa.Column('driver_id', sa.Uuid(), nullable=False),
        sa.Column('party_id', sa.Uuid(), nullable=False),
        sa.Column('quarry_id', sa.Uuid(), nullable=False),
        sa.Column('material_id', sa.Uuid(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('purchase_rate', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('purchase_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('sale_rate', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('sale_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('transport_expense', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('other_expense', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('net_profit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_type', sa.String(length=20), nullable=False),
        sa.Column('cash_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('debit_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tractor_id'], ['tractors.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['party_id'], ['parties.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['quarry_id'], ['quarries.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('quantity >= 0', name='chk_trips_quantity'),
        sa.CheckConstraint('purchase_rate >= 0', name='chk_trips_purchase_rate'),
        sa.CheckConstraint('purchase_amount >= 0', name='chk_trips_purchase_amount'),
        sa.CheckConstraint('sale_rate >= 0', name='chk_trips_sale_rate'),
        sa.CheckConstraint('sale_amount >= 0', name='chk_trips_sale_amount'),
        sa.CheckConstraint('transport_expense >= 0', name='chk_trips_transport_expense'),
        sa.CheckConstraint('other_expense >= 0', name='chk_trips_other_expense'),
        sa.CheckConstraint('cash_amount >= 0', name='chk_trips_cash_amount'),
        sa.CheckConstraint('debit_amount >= 0', name='chk_trips_debit_amount'),
    )
    op.create_index('ix_trips_trip_number', 'trips', ['trip_number'], unique=False)
    op.create_index('uq_trips_trip_number', 'trips', ['trip_number'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'expenses'
    op.create_table(
        'expenses',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('category_id', sa.Uuid(), nullable=False),
        sa.Column('tractor_id', sa.Uuid(), nullable=True),
        sa.Column('trip_id', sa.Uuid(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('recipient', sa.String(length=150), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('receipt_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['expense_categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['tractor_id'], ['tractors.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('amount > 0', name='chk_expenses_amount'),
    )
    op.create_index('idx_expenses_date', 'expenses', ['expense_date'], unique=False)

    # 'payments'
    op.create_table(
        'payments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('payment_number', sa.String(length=50), nullable=False),
        sa.Column('payment_type', postgresql.ENUM('receipt', 'disbursement', name='payment_type_enum', create_type=False), nullable=False),
        sa.Column('payment_mode', postgresql.ENUM('cash', 'bank_transfer', 'upi', 'cheque', 'credit_card', name='payment_mode_enum', create_type=False), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('trip_id', sa.Uuid(), nullable=True),
        sa.Column('party_id', sa.Uuid(), nullable=True),
        sa.Column('driver_id', sa.Uuid(), nullable=True),
        sa.Column('expense_category_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['party_id'], ['parties.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['expense_category_id'], ['expense_categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('amount > 0', name='chk_payments_amount'),
        sa.CheckConstraint('(party_id IS NOT NULL) OR (driver_id IS NOT NULL) OR (trip_id IS NOT NULL) OR (expense_category_id IS NOT NULL)', name='chk_payments_target_not_empty'),
    )
    op.create_index('ix_payments_payment_number', 'payments', ['payment_number'], unique=False)
    op.create_index('ix_payments_reference_number', 'payments', ['reference_number'], unique=False)
    op.create_index('uq_payments_payment_number', 'payments', ['payment_number'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # 'audit_logs'
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('action', sa.String(length=10), nullable=False),
        sa.Column('table_name', sa.String(length=100), nullable=False),
        sa.Column('record_id', sa.Uuid(), nullable=False),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)
    op.create_index('idx_audit_logs_target_record', 'audit_logs', ['table_name', 'record_id'], unique=False)

    # 'notifications'
    op.create_table(
        'notifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', postgresql.ENUM('alert', 'system', 'info', 'expiry_reminder', 'payment_reminder', name='notification_type_enum', create_type=False), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version_id', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_notifications_unread', 'notifications', ['user_id', 'read_at'], unique=False, postgresql_where=sa.text('read_at IS NULL'))


def downgrade():
    # 1. Drop tables in reverse topological dependency order
    op.drop_table('notifications')
    op.drop_table('audit_logs')
    op.drop_table('payments')
    op.drop_table('expenses')
    op.drop_table('trips')
    op.drop_table('drivers')
    op.drop_table('refresh_tokens')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('expense_categories')
    op.drop_table('materials')
    op.drop_table('quarries')
    op.drop_table('parties')
    op.drop_table('tractors')
    op.drop_table('settings')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')

    # 2. Drop PostgreSQL native enum types
    op.execute("DROP TYPE notification_type_enum")
    op.execute("DROP TYPE payment_mode_enum")
    op.execute("DROP TYPE payment_type_enum")
    op.execute("DROP TYPE tractor_status_enum")
    op.execute("DROP TYPE driver_status_enum")
