from fastapi import HTTPException, APIRouter, status
from typing import List
from bson import ObjectId
from datetime import datetime
from src.database import Vehicle
from src.models import VehicleModel
from src.schemas import ErrorResponseMessage, VehicleRead

router = APIRouter()


@router.get(
    "/vehicles",
    response_model=List[VehicleRead],
)
async def read_vehicles():
    return await Vehicle.find().to_list(length=None)


@router.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleRead,
    responses={
        400: {"model": ErrorResponseMessage},
    },
)
async def read_vehicle(vehicle_id: str):
    # Check the existing vehicle
    vehicle = await Vehicle.find_one({"_id": ObjectId(vehicle_id)})
    if vehicle:
        return vehicle
    else:
        raise HTTPException(status_code=400, detail="Vehicle not found!")


@router.post(
    "/vehicles",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseMessage},
    },
)
async def add_vehicle(vehicle: VehicleModel):
    # Check if the vehicle or driver already exists in the database
    existing_vehicle_or_driver = await Vehicle.find_one(
        {
            "$or": [
                {"registration_number": vehicle.registration_number},
                {"driver_license_number": vehicle.driver_license_number},
            ]
        }
    )

    if existing_vehicle_or_driver:
        # Check which field is causing the conflict and raise an appropriate error
        if (
            existing_vehicle_or_driver["registration_number"]
            == vehicle.registration_number
        ):
            raise HTTPException(
                status_code=400, detail="This vehicle is already assigned to a driver."
            )
        if (
            existing_vehicle_or_driver["driver_license_number"]
            == vehicle.driver_license_number
        ):
            raise HTTPException(
                status_code=400,
                detail="This driver is already assigned to another vehicle.",
            )

    vehicle_dict = vehicle.model_dump()
    vehicle_dict["created_at"] = datetime.now()
    vehicle_dict["updated_at"] = None

    try:
        result = await Vehicle.insert_one(vehicle_dict)
        vehicle_dict["_id"] = result.inserted_id  # Capture the MongoDB _id
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error inserting vehicle!")

    return vehicle_dict
