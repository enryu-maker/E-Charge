from fastapi import FastAPI, status
from app.database import engine, Base
from app.routes import user, vehicle
from app.models.user import User
app = FastAPI(
    title="E-Chagre",
    description="FastAPI backend for E-charge Application",
    version="1.0.0",
)


Base.metadata.create_all(bind=engine)


@app.get('/system-status', status_code=status.HTTP_200_OK)
async def read_root():
    return {"message": {
        "status": True,
        "description": "API is running"
    }}  # type: ignore


app.include_router(user.router)
app.include_router(vehicle.router)
