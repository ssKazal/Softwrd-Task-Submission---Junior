from datetime import datetime
from pydantic import BaseModel, EmailStr


class EmployeeModel(BaseModel):
    """
    Model for a single employee record.
    """

    name: str
    email: EmailStr


class VehicleModel(BaseModel):
    """
    Model for a single vehicle record.
    """

    name: str
    registration_number: str
    driver_name: str
    driver_license_number: str


class AllocationModel(BaseModel):
    """
    Model for a single allocation record.
    """

    employee_id: str | None
    vehicle_id: str | None
    allocation_date: datetime


class AllocationLogModel(BaseModel):
    """
    Model for a single allocation log record.
    """

    allocation_id: str | None
    employee_id: str | None
    vehicle_id: str | None
    allocation_date: datetime
    action: str  # e.g., "created", "updated", "deleted"
