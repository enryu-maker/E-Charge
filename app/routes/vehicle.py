from fastapi import APIRouter, status, HTTPException, Depends
from app.database import SessionLocale
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.vehicle import VehicleResponse, VehicleCreate
from app.service.user_service import decode_access_token
router = APIRouter(prefix="/api/vehicle", tags=["Vehicle API"])


def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()


db_depandancy = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(decode_access_token)]


@router.get("/get-vehicles/", response_model=List[VehicleResponse])
async def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).all()
    return vehicles


@router.post("/create-vehicle/", response_model=VehicleResponse)
async def create_vehicle(user: user_dependancy, vehicle: VehicleCreate, db: Session = Depends(get_db)):

    if user:
        db_user = db.query(User).filter(
            User.id == user.get("user_id")).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if the user is a vendor
        if db_user.user_type == 'vendor':
            # Ensure charging_price is provided by the vendor
            if not vehicle.charging_price:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Vendors must provide charging price based on percentage")
        else:
            # Non-vendors cannot set charging_price
            if vehicle.charging_price:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Only vendors can set charging prices")

        db_vehicle = Vehicle(**vehicle.model_dump(), user_id=db_user.id)
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")
