from enum import Enum

class PermissionModule(str, Enum):
    AUTH = "AUTH"
    USERS = "USERS"
    ROLES = "ROLES"
    DRIVERS = "DRIVERS"
    TRACTORS = "TRACTORS"
    TRIPS = "TRIPS"
    INVOICES = "INVOICES"
    MAINTENANCE = "MAINTENANCE"
    FUEL = "FUEL"
    REPORTS = "REPORTS"
    SETTINGS = "SETTINGS"
