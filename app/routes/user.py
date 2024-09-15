from fastapi import APIRouter, status, HTTPException, Depends, Query
from app.database import SessionLocale
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, OTPVerify, UserResponse
from app.schemas.vehicle import VendorVehicleResponse
from app.models.user import User
from app.models.vehicle import Vehicle
from typing import Annotated, List
import os
import math
from datetime import timedelta
from dotenv import load_dotenv
from app.service.user_service import generate_otp, create_accesss_token, send_otp, decode_access_token, calculate_distance

load_dotenv()
API_KEY = os.getenv("API_KEY")

router = APIRouter(prefix="/api/user", tags=["User API"])


def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()


db_depandancy = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(decode_access_token)]


@router.get('/get-users', response_model=List[UserResponse])
async def get_user(db: db_depandancy):
    user = db.query(User).all()
    return user


@router.delete('/delete-users')
async def get_user(db: db_depandancy):
    user = db.query(User).all()
    for i in user:
        db.delete(i)
        db.commit()
    return {"message": "users deleted"}


@router.get('/get-profile', response_model=UserResponse)
async def get_user(user: user_dependancy, db: db_depandancy):
    if user:
        user = db.query(User).filter(
            User.id == user.get("user_id")).first()
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")


@router.get('/search-vendors/')
async def search_vendors(
    user_lat: float = Query(..., ge=-90, le=90),  # User's latitude
    user_long: float = Query(..., ge=-180, le=180),  # User's longitude
    make: str = Query(None),  # Vehicle make to search
    model: str = Query(None),  # Vehicle model to search
    db: Session = Depends(get_db)
):
    # Fetch all vendors that have vehicles matching the make and model
    query = db.query(User).join(Vehicle).filter(User.user_type == 'vendor')

    if make:
        query = query.filter(Vehicle.make.ilike(f'%{make}%'))
    if model:
        query = query.filter(Vehicle.model.ilike(f'%{model}%'))

    vendors = query.all()

    # Calculate the distance between the user's location and each vendor's location
    vendor_distances = []
    for vendor in vendors:
        if vendor.latitude is None or vendor.longitude is None:
            continue  # Skip vendors with no latitude/longitude

        distance = calculate_distance(
            user_lat, user_long, vendor.latitude, vendor.longitude)
        vendor_distances.append({
            "vendor": vendor,
            "distance": distance
        })

    # Sort vendors by distance
    sorted_vendors = sorted(vendor_distances, key=lambda x: x["distance"])

    # Return a list of vendors sorted by distance
    return [
        {
            "vendor_name": vendor["vendor"].full_name,
            "mobile_number": vendor["vendor"].mobile_number,
            "latitude": vendor["vendor"].latitude,
            "longitude": vendor["vendor"].longitude,
            "distance_km": round(vendor["distance"], 2)
        }
        for vendor in sorted_vendors
    ]


@router.post('/create-user', status_code=status.HTTP_201_CREATED)
async def createUser(user: UserCreate, db: db_depandancy):
    db_user = db.query(User).filter(
        User.mobile_number == user.mobile_number).first()
    if db_user and db_user.is_verified == False:
        try:
            otp_status = send_otp(db_user.otp, db_user.mobile_number)
            if otp_status:
                return {"message": "otp sent"}
            else:
                return {"message": "otp not sent"}
        except Exception as e:
            return {"msg": e}

    # Generate OTP and set expiration
    otp = generate_otp()
    if user.user_type == "vendor":
        if user.latitude is None or user.longitude is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Vendors must provide latitude and longitude")
        new_user = User(
            full_name=user.full_name,
            mobile_number=user.mobile_number,
            otp=otp,
            user_type=user.user_type,
            latitude=user.latitude,
            longitude=user.longitude
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    else:
        new_user = User(
            full_name=user.full_name,
            mobile_number=user.mobile_number,
            otp=otp,
            user_type=user.user_type
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    try:
        otp_status = send_otp(otp, new_user.mobile_number)
        if otp_status:
            return {"message": "otp sent"}
        else:
            return {"message": "otp not sent"}
    except Exception as e:

        return {"msg": e}


@router.post('/verify-user', status_code=status.HTTP_200_OK)
async def verifyUser(data: OTPVerify, db: db_depandancy):
    db_user = db.query(User).filter(
        User.mobile_number == data.mobile_number).first()

    if not db_user:
        raise HTTPException(
            status_code=400, detail="User not found")

    if db_user.otp != data.otp:
        raise HTTPException(
            status_code=400, detail="Invalid OTP")
    db_user.is_verified = True
    db.commit()
    access = create_accesss_token(
        db_user.full_name, db_user.id, timedelta(days=90))
    return {
        "msg": "OTP verified successfull",
        "access_token": access,
        "user": {
            "full_name": db_user.full_name,
            "mobile_number": db_user.mobile_number,
            "user_type": db_user.user_type,
        }
    }


@router.post('/login-user', status_code=status.HTTP_200_OK)
async def login_user(mobile_number: str, db: db_depandancy):
    db_user = db.query(User).filter(
        User.mobile_number == mobile_number).first()
    if not db_user:
        raise HTTPException(
            status_code=400, detail="User not found")
    otp = generate_otp()
    db_user.otp = otp
    db.add(db_user)
    db.commit()
    try:
        otp_status = send_otp(otp, db_user.mobile_number)
        if otp_status:
            return {"message": "otp sent"}
        else:
            return {"message": "otp not sent"}
    except Exception as e:

        return {"msg": e}
