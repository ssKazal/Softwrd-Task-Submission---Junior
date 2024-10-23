from fastapi import HTTPException, APIRouter, status
from datetime import datetime
from typing import List
from bson import ObjectId
from src.database import Employee
from src.models import EmployeeModel
from src.schemas import ErrorResponseMessage, EmployeeRead

router = APIRouter()


@router.get(
    "/employees",
    response_model=List[EmployeeRead],
)
async def read_employees():
    return await Employee.find().to_list(length=None)


@router.get(
    "/employees/{employee_id}",
    response_model=EmployeeRead,
    responses={
        400: {"model": ErrorResponseMessage},
    },
)
async def read_employee(employee_id: str):
    # Check the existing employee
    employee = await Employee.find_one({"_id": ObjectId(employee_id)})
    if employee:
        return employee
    else:
        raise HTTPException(status_code=400, detail="Employee not found!")


@router.post(
    "/employees",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseMessage},
    },
)
async def add_employee(employee: EmployeeModel):
    # Check if the email already exists
    existing_employee = await Employee.find_one({"email": employee.email})
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email already exists!")

    employee_dict = employee.model_dump()
    employee_dict["created_at"] = datetime.now()
    employee_dict["updated_at"] = None

    try:
        result = await Employee.insert_one(employee_dict)
        employee_dict["_id"] = result.inserted_id  # Capture the MongoDB _id
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error inserting employee!")

    return employee_dict
