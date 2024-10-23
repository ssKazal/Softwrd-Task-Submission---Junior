from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import BeforeValidator
from typing import Optional, Annotated
from datetime import datetime

# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


# Global schema for error message
class ErrorResponseMessage(BaseModel):
    detail: str


class MinimumEmployeeRead(BaseModel):
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class EmployeeRead(BaseModel):
    # Provided as `_id` as str in the API responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class MinimumVehicleRead(BaseModel):
    name: str
    driver_name: str

    class Config:
        from_attributes = True


class VehicleRead(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    registration_number: str
    driver_name: str
    driver_license_number: str
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class AllocationRead(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    employee: MinimumEmployeeRead | None
    vehicle: MinimumVehicleRead | None
    allocation_date: datetime
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class AllocationLogRead(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    allocation_id: str
    employee_id: str | None
    vehicle_id: str | None
    allocation_date: datetime
    action: str
    created_at: datetime | None

    class Config:
        from_attributes = True
