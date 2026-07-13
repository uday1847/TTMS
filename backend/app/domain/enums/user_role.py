from enum import StrEnum


class UserRole(StrEnum):
    """
    Defines the roles available in the Transport Tractor Management System (TTMS)
    for RBAC (Role-Based Access Control).
    """
    ADMIN = "admin"
    DISPATCHER = "dispatcher"
    DRIVER = "driver"
    ACCOUNTANT = "accountant"
