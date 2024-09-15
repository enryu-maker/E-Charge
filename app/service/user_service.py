import random
import string
import datetime
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from jose import jwt, JWTError
import requests
from typing import Annotated
from math import radians, cos, sin, sqrt, atan2

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/user/verify-user')


def generate_otp():
    return ''.join(random.choices(string.digits, k=4))


def send_otp(otp: str, mobile_number: str) -> bool:

    url = f'https://2factor.in/API/V1/74380642-1da4-11ef-8b60-0200cd936042/SMS/{mobile_number}/{otp}'
    print(url)
    payload = {}
    headers = {}

    response = requests.request(
        "GET", url,
        headers=headers, data=payload)
    if response.status_code == 200:
        return True
    return False


def create_accesss_token(username: str, user_id: int, expiry: timedelta):
    encode = {
        'sub':  username,
        'id': user_id
    }
    expires = datetime.datetime.utcnow() + expiry
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get('sub')
        user_id: int = payload.get('id')
        if name is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid access token")
        return {
            'name': name,
            'user_id': user_id
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2)**2 + cos(radians(lat1)) * \
        cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # Distance in kilometers
    return distance
