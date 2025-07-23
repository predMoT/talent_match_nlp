from fastapi import Request, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

def get_database(request: Request) -> AsyncIOMotorDatabase:
    """
    FastAPI dependency - MongoDB veritabanı bağlantısını döner
    """
    return request.app.state.database