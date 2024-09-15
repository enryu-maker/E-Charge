from sqlalchemy import String, Integer, Boolean, Column, ForeignKey, DateTime, Float
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    mobile_number = Column(String, unique=True, index=True)
    otp = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    user_type = Column(String, nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    vehicles = relationship("Vehicle", back_populates="user")
