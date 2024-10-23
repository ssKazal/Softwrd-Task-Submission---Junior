from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings
from pymongo import ASCENDING

client = AsyncIOMotorClient(settings.database_url)
db = client[settings.mongo_initdb_database]

# Collections
Employee = db.employees
Vehicle = db.vehicles
Allocation = db.allocations
AllocationLog = db.allocation_logs


# Indexes are created asynchronously
async def create_indexes():
    await Employee.create_index([("email", ASCENDING)], unique=True)
    await Vehicle.create_index(
        [("registration_number", ASCENDING), ("driver_license_number", ASCENDING)],
        unique=True,
    )
    await AllocationLog.create_index([("allocation_date", ASCENDING)])
