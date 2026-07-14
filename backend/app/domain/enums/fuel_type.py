from enum import Enum


class FuelType(str, Enum):
    DIESEL = "DIESEL"
    PETROL = "PETROL"
    CNG = "CNG"
    LNG = "LNG"
    ELECTRIC = "ELECTRIC"
    OTHER = "OTHER"
