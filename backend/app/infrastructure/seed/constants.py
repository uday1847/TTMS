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

# Permission Seeding Constants (Permission IDs)
PERMISSION_USER_CREATE_ID = uuid.UUID("00000000-0000-0000-0000-000000000201")
PERMISSION_USER_READ_ID = uuid.UUID("00000000-0000-0000-0000-000000000202")
PERMISSION_USER_UPDATE_ID = uuid.UUID("00000000-0000-0000-0000-000000000203")
PERMISSION_USER_DELETE_ID = uuid.UUID("00000000-0000-0000-0000-000000000204")
PERMISSION_VEHICLE_CREATE_ID = uuid.UUID("00000000-0000-0000-0000-000000000205")
PERMISSION_VEHICLE_UPDATE_ID = uuid.UUID("00000000-0000-0000-0000-000000000206")
PERMISSION_DRIVER_CREATE_ID = uuid.UUID("00000000-0000-0000-0000-000000000207")
PERMISSION_CUSTOMER_CREATE_ID = uuid.UUID("00000000-0000-0000-0000-000000000208")

PERMISSION_DEFINITIONS = [
    {
        "id": PERMISSION_USER_CREATE_ID,
        "code": "User.Create",
        "description": "Ability to create new system users.",
    },
    {
        "id": PERMISSION_USER_READ_ID,
        "code": "User.Read",
        "description": "Ability to read and view user directories.",
    },
    {
        "id": PERMISSION_USER_UPDATE_ID,
        "code": "User.Update",
        "description": "Ability to edit and update existing user accounts.",
    },
    {
        "id": PERMISSION_USER_DELETE_ID,
        "code": "User.Delete",
        "description": "Ability to soft-delete or disable user profiles.",
    },
    {
        "id": PERMISSION_VEHICLE_CREATE_ID,
        "code": "Vehicle.Create",
        "description": "Ability to register new fleet tractors and trailers.",
    },
    {
        "id": PERMISSION_VEHICLE_UPDATE_ID,
        "code": "Vehicle.Update",
        "description": "Ability to edit parameters of active fleet assets.",
    },
    {
        "id": PERMISSION_DRIVER_CREATE_ID,
        "code": "Driver.Create",
        "description": "Ability to register vehicle drivers and licensing terms.",
    },
    {
        "id": PERMISSION_CUSTOMER_CREATE_ID,
        "code": "Customer.Create",
        "description": "Ability to register new customer billing accounts.",
    },
]

# Super Admin Seeding Constants
SUPER_ADMIN_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000100")
