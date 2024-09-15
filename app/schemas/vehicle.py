from pydantic import BaseModel
from typing import Optional, Dict


class VehicleBase(BaseModel):
    make: str
    model: str
    year: int
    battery_capacity: Optional[str] = None  # New field
    charging_price: Optional[Dict[str, int]] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    user_id: Optional[int] = None  # Optional if not included in all responses
    charging_price: Optional[Dict[str, int]] = None

    class Config:
        orm_mode = True


class VendorVehicleResponse(BaseModel):
    id: int
    make: str
    model: str
    year: int
    battery_capacity: Optional[str] = None
    charging_price: Optional[Dict[str, int]] = None

    class Config:
        orm_mode = True
