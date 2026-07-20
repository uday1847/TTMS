from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class BaseDTO(BaseModel):
    """
    Base Data Transfer Object for all application boundaries.
    Automatically handles camelCase serialization and deserialization
    for strict alignment with frontend TypeScript conventions.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra='forbid',
        str_strip_whitespace=True,
    )
