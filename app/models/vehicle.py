from sqlalchemy import String, Integer, Boolean, Column, ForeignKey, JSON
from app.database import Base
from sqlalchemy.orm import relationship


class Vehicle(Base):
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    battery_capacity = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Link to the User model
    charging_price = Column(JSON, nullable=True)
    user = relationship("User", back_populates="vehicles")
