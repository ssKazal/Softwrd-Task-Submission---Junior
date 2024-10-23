from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database import create_indexes
from src.routers import allocation, employee, vehicle
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await create_indexes()  # Create indexes when app starts
    redis = aioredis.from_url("redis://redis:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Vehicle Allocation System",
    description="API for managing vehicle allocations for employees",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Vehicle Allocation System"}


app.include_router(allocation.router, tags=["Allocation"], prefix="/api")
app.include_router(employee.router, tags=["Employee"], prefix="/api")
app.include_router(vehicle.router, tags=["Vehicle"], prefix="/api")
