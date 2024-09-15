from pydantic import BaseModel, Field
from typing import List, Optional
from .vehicle import VehicleResponse


class UserResponse(BaseModel):
    id: int
    full_name: str
    mobile_number: str
    is_verified: bool
    user_type: str
    vehicles: List[VehicleResponse] = []
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        orm_mode = True  # Allows the Pydantic model to work with SQLAlchemy objects


class UserCreate(BaseModel):
    full_name: str
    mobile_number: str
    user_type: str
    latitude: Optional[float] = Field(
        None, ge=-90, le=90)  # Latitude range: -90 to 90
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class OTPVerify(BaseModel):
    mobile_number: str
    otp: str
