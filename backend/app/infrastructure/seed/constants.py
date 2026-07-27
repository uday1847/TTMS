import uuid

# System Seeding Constants (System User)
SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Role Seeding Constants (Role IDs)
SUPER_ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
MANAGER_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000012")
ACCOUNTANT_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000013")
DISPATCHER_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000014")
DRIVER_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000015")
OPERATOR_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000016")
CUSTOMER_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000017")

ROLE_DEFINITIONS = [
    {
        "id": SUPER_ADMIN_ROLE_ID,
        "name": "Super Admin",
        "display_name": "Super Administrator",
        "description": "Unrestricted system-wide access to all configurations and operations.",
    },
    {
        "id": ADMIN_ROLE_ID,
        "name": "Admin",
        "display_name": "Administrator",
        "description": "Administrative access to manage users, configurations, and fleet parameters.",
    },
    {
        "id": MANAGER_ROLE_ID,
        "name": "Manager",
        "display_name": "Manager",
        "description": "Operational manager oversight, analytics access, and rate approval permissions.",
    },
    {
        "id": ACCOUNTANT_ROLE_ID,
        "name": "Accountant",
        "display_name": "Accountant",
        "description": "Financial operations oversight, ledger access, invoicing, and expense approval.",
    },
    {
        "id": DISPATCHER_ROLE_ID,
        "name": "Dispatcher",
        "display_name": "Dispatcher",
        "description": "Manage trips, assign drivers, log quarries, and coordinate shipments.",
    },
    {
        "id": DRIVER_ROLE_ID,
        "name": "Driver",
        "display_name": "Driver",
        "description": "Log trip details, report expenses, and check payroll status.",
    },
    {
        "id": OPERATOR_ROLE_ID,
        "name": "Operator",
        "display_name": "Operator",
        "description": "Record tractor operational telemetry and yard management details.",
    },
    {
        "id": CUSTOMER_ROLE_ID,
        "name": "Customer",
        "display_name": "Customer",
        "description": "View assigned shipments, delivery timelines, and associated invoices.",
    },
]

# Permission Seeding Constants
PERMISSION_DEFINITIONS = [
    {"id": uuid.uuid4(), "code": "users:read", "description": "Read users"},
    {"id": uuid.uuid4(), "code": "users:create", "description": "Create users"},
    {"id": uuid.uuid4(), "code": "users:update", "description": "Update users"},
    {"id": uuid.uuid4(), "code": "users:delete", "description": "Delete users"},
    {"id": uuid.uuid4(), "code": "users:role_assign", "description": "Assign roles to users"},
    {"id": uuid.uuid4(), "code": "drivers:read", "description": "Read drivers"},
    {"id": uuid.uuid4(), "code": "drivers:create", "description": "Create drivers"},
    {"id": uuid.uuid4(), "code": "drivers:update", "description": "Update drivers"},
    {"id": uuid.uuid4(), "code": "drivers:delete", "description": "Delete drivers"},
    {"id": uuid.uuid4(), "code": "tractors:read", "description": "Read tractors"},
    {"id": uuid.uuid4(), "code": "tractors:create", "description": "Create tractors"},
    {"id": uuid.uuid4(), "code": "tractors:update", "description": "Update tractors"},
    {"id": uuid.uuid4(), "code": "tractors:delete", "description": "Delete tractors"},
    {"id": uuid.uuid4(), "code": "trips:read", "description": "Read trips"},
    {"id": uuid.uuid4(), "code": "trips:create", "description": "Create trips"},
    {"id": uuid.uuid4(), "code": "trips:update", "description": "Update trips"},
    {"id": uuid.uuid4(), "code": "trips:delete", "description": "Delete trips"},
    {"id": uuid.uuid4(), "code": "parties:read", "description": "Read parties"},
    {"id": uuid.uuid4(), "code": "parties:create", "description": "Create parties"},
    {"id": uuid.uuid4(), "code": "parties:update", "description": "Update parties"},
    {"id": uuid.uuid4(), "code": "parties:delete", "description": "Delete parties"},
    {"id": uuid.uuid4(), "code": "expenses:read", "description": "Read expenses"},
    {"id": uuid.uuid4(), "code": "expenses:create", "description": "Create expenses"},
    {"id": uuid.uuid4(), "code": "expenses:update", "description": "Update expenses"},
    {"id": uuid.uuid4(), "code": "expenses:delete", "description": "Delete expenses"},
    {"id": uuid.uuid4(), "code": "permissions:read", "description": "Read permissions"},
    {"id": uuid.uuid4(), "code": "permissions:create", "description": "Create permissions"},
    {"id": uuid.uuid4(), "code": "permissions:update", "description": "Update permissions"},
    {"id": uuid.uuid4(), "code": "permissions:delete", "description": "Delete permissions"},
    {"id": uuid.uuid4(), "code": "roles:read", "description": "Read roles"},
    {"id": uuid.uuid4(), "code": "roles:create", "description": "Create roles"},
    {"id": uuid.uuid4(), "code": "roles:update", "description": "Update roles"},
    {"id": uuid.uuid4(), "code": "roles:delete", "description": "Delete roles"},
    {"id": uuid.uuid4(), "code": "roles:permission_assign", "description": "Assign permissions to roles"},
]

# Super Admin Seeding Constants
SUPER_ADMIN_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000100")
