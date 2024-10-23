from fastapi import HTTPException, APIRouter, status, Query
from datetime import datetime
from typing import List
from bson import ObjectId
from src.database import Allocation, AllocationLog, Employee, Vehicle
from src.models import AllocationModel, AllocationLogModel
from src.schemas import (
    ErrorResponseMessage,
    AllocationRead,
    AllocationLogRead,
    MinimumEmployeeRead,
    MinimumVehicleRead,
)
from fastapi_cache.decorator import cache

router = APIRouter()


async def get_allocation_by_id(allocation_id: str):
    # Check if the allocation exists
    allocation = await Allocation.find_one({"_id": ObjectId(allocation_id)})
    if allocation:
        return allocation
    else:
        raise HTTPException(status_code=404, detail="Allocation not found!")


# List view
@router.get(
    "/allocations",
    response_model=List[AllocationRead],
)
@cache(expire=60)
async def read_allocations(offset: int = 0, limit: int = 10):
    allocations = await Allocation.find().skip(offset).limit(limit).to_list()
    allocation_list = []

    for allocation in allocations:
        employee = await Employee.find_one({"_id": ObjectId(allocation["employee_id"])})
        vehicle = await Vehicle.find_one({"_id": ObjectId(allocation["vehicle_id"])})

        allocation_data = AllocationRead(
            _id=str(allocation["_id"]),
            employee=MinimumEmployeeRead(**employee) if employee else None,
            vehicle=MinimumVehicleRead(**vehicle) if vehicle else None,
            allocation_date=allocation["allocation_date"],
            created_at=allocation["created_at"],
            updated_at=allocation["updated_at"],
        )
        allocation_list.append(allocation_data)

    return allocation_list


# Detail View
@router.get(
    "/allocations/{allocation_id}",
    response_model=AllocationRead,
    responses={
        404: {"model": ErrorResponseMessage},
    },
)
@cache(expire=60)
async def read_allocation(allocation_id: str):
    allocation = await get_allocation_by_id(allocation_id)
    employee = await Employee.find_one({"_id": ObjectId(allocation["employee_id"])})
    vehicle = await Vehicle.find_one({"_id": ObjectId(allocation["vehicle_id"])})

    allocation_data = AllocationRead(
        _id=str(allocation["_id"]),
        employee=MinimumEmployeeRead(**employee) if employee else None,
        vehicle=MinimumVehicleRead(**vehicle) if vehicle else None,
        allocation_date=allocation["allocation_date"],
        created_at=allocation.get("created_at"),
        updated_at=allocation.get("updated_at"),
    )

    return allocation_data


# Create view
@router.post(
    "/allocations",
    response_model=AllocationRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseMessage},
    },
)
async def allocate_vehicle(allocation: AllocationModel):
    # Ensure allocation date is in the future
    if allocation.allocation_date.date() < datetime.now().date():
        raise HTTPException(
            status_code=400, detail="Allocation date must be in the future!"
        )

    # Check if the vehicle is already allocated or if the employee has already allocated a vehicle for the same date
    existing_allocation = await Allocation.find_one(
        {
            "$or": [
                {
                    "vehicle_id": allocation.vehicle_id,
                    "allocation_date": allocation.allocation_date,
                },
                {
                    "employee_id": allocation.employee_id,
                    "allocation_date": allocation.allocation_date,
                },
            ]
        }
    )

    if existing_allocation:
        # Determine which condition was violated
        if existing_allocation["vehicle_id"] == allocation.vehicle_id:
            raise HTTPException(
                status_code=400, detail="Vehicle is already allocated for a day!"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Employee can only allocate one vehicle per day!",
            )

    allocation_dict = allocation.model_dump()
    allocation_dict["created_at"] = datetime.now()
    allocation_dict["updated_at"] = None

    try:
        # Insert the new allocation into the database
        result = await Allocation.insert_one(allocation_dict)
        allocation_dict["_id"] = result.inserted_id

        # Fetch Employee and Vehicle details
        employee = await Employee.find_one({"_id": ObjectId(allocation.employee_id)})
        vehicle = await Vehicle.find_one({"_id": ObjectId(allocation.vehicle_id)})

        # Nesting the details into the response
        allocation_dict["employee"] = (
            MinimumEmployeeRead(**employee) if employee else None
        )
        allocation_dict["vehicle"] = MinimumVehicleRead(**vehicle) if vehicle else None
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error inserting allocation!")

    # Record the action in allocation log
    log_entry = AllocationLogModel(
        allocation_id=str(allocation_dict["_id"]),
        employee_id=allocation_dict["employee_id"],
        vehicle_id=allocation_dict["vehicle_id"],
        allocation_date=allocation_dict["allocation_date"],
        action="created",
    )
    allocation_log_dict = log_entry.model_dump()
    allocation_log_dict["created_at"] = datetime.now()
    try:
        # Insert the new allocation log into the database
        result = await AllocationLog.insert_one(allocation_log_dict)
        allocation_log_dict["_id"] = result.inserted_id
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error inserting allocation log!")

    return allocation_dict


# Update view
@router.put(
    "/allocations/{allocation_id}",
    response_model=AllocationRead,
    responses={
        400: {"model": ErrorResponseMessage},
        404: {"model": ErrorResponseMessage},
    },
)
async def update_allocation(allocation_id: str, allocation: AllocationModel):
    # Check if the allocation exists
    existing_allocation = await get_allocation_by_id(allocation_id)

    # Ensure allocation date is in the future
    if allocation.allocation_date.date() < datetime.now().date():
        raise HTTPException(
            status_code=400, detail="Allocation date must be in the future!"
        )

    # Check for conflicts with vehicle and employee
    conflicting_allocation = await Allocation.find_one(
        {
            "$or": [
                {
                    "vehicle_id": allocation.vehicle_id,
                    "allocation_date": allocation.allocation_date,
                },
                {
                    "employee_id": allocation.employee_id,
                    "allocation_date": allocation.allocation_date,
                },
            ],
        }
    )

    if conflicting_allocation and conflicting_allocation["_id"] != ObjectId(
        allocation_id
    ):
        # Determine which condition was violated
        if conflicting_allocation["vehicle_id"] == allocation.vehicle_id:
            raise HTTPException(
                status_code=400, detail="Vehicle is already allocated for this date!"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Employee can only allocate one vehicle per day!",
            )

    # Update allocation details
    allocation_dict = allocation.model_dump()
    allocation_dict["created_at"] = existing_allocation["created_at"]
    allocation_dict["updated_at"] = datetime.now()

    try:
        # Update the allocation in the database
        await Allocation.update_one(
            {"_id": ObjectId(allocation_id)}, {"$set": allocation_dict}
        )
        allocation_dict["_id"] = allocation_id

        # Fetch Employee and Vehicle details
        employee = await Employee.find_one({"_id": ObjectId(allocation.employee_id)})
        vehicle = await Vehicle.find_one({"_id": ObjectId(allocation.vehicle_id)})

        # Nesting the details into the response
        allocation_dict["employee"] = (
            MinimumEmployeeRead(**employee) if employee else None
        )
        allocation_dict["vehicle"] = MinimumVehicleRead(**vehicle) if vehicle else None
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error updating allocation!")

    # Record the action in allocation log
    log_entry = AllocationLogModel(
        allocation_id=str(allocation_dict["_id"]),
        employee_id=allocation_dict["employee_id"],
        vehicle_id=allocation_dict["vehicle_id"],
        allocation_date=allocation_dict["allocation_date"],
        action="updated",
    )
    allocation_log_dict = log_entry.model_dump()
    allocation_log_dict["created_at"] = datetime.now()
    try:
        # Insert the new allocation log into the database
        result = await AllocationLog.insert_one(allocation_log_dict)
        allocation_log_dict["_id"] = result.inserted_id
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error inserting allocation log!")

    return allocation_dict


# Delete View
@router.delete(
    "/allocations/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Allocation deleted successfully"},
        400: {"model": ErrorResponseMessage},
        404: {"model": ErrorResponseMessage},
    },
)
async def delete_allocation(allocation_id: str):
    allocation = await get_allocation_by_id(allocation_id)

    # Check if the allocation date is in the past
    if allocation["allocation_date"].date() >= datetime.now().date():
        raise HTTPException(
            status_code=400, detail="Cannot delete allocations that are unfinished!"
        )

    # Record the action in allocation log
    log_entry = AllocationLogModel(
        allocation_id=str(allocation["_id"]),
        employee_id=allocation["employee_id"],
        vehicle_id=allocation["vehicle_id"],
        allocation_date=allocation["allocation_date"],
        action="deleted",
    )

    # Proceed to delete the allocation
    await Allocation.delete_one({"_id": ObjectId(allocation["_id"])})

    allocation_log_dict = log_entry.model_dump()
    allocation_log_dict["created_at"] = datetime.now()
    try:
        # Insert the new allocation log into the database
        result = await AllocationLog.insert_one(allocation_log_dict)
        allocation_log_dict["_id"] = result.inserted_id
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error inserting allocation log!")


@router.get("/allocation/logs", response_model=List[AllocationLogRead])
@cache(expire=60)
async def read_allocation_logs(
    employee_id: str = None,
    vehicle_id: str = None,
    action: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    offset: int = Query(0, ge=0),  # Ensure offset is non-negative,
    limit: int = Query(10, ge=1, le=100),  # Limit results with sensible default
):
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if vehicle_id:
        query["vehicle_id"] = vehicle_id
    if action:
        query["action"] = action
    if start_date and end_date:
        query["allocation_date"] = {"$gte": start_date, "$lte": end_date}

    # Fetch logs from the AllocationLog collection
    logs = await AllocationLog.find(query).skip(offset).limit(limit).to_list()

    allocation_logs = []
    for log in logs:

        # Create the AllocationLogRead object
        allocation_log = AllocationLogRead(
            _id=str(log["_id"]),
            allocation_id=log["allocation_id"],
            employee_id=log["employee_id"],
            vehicle_id=log["vehicle_id"],
            allocation_date=log["allocation_date"],
            action=log["action"],
            created_at=log["created_at"],
        )
        allocation_logs.append(allocation_log)

    return allocation_logs
