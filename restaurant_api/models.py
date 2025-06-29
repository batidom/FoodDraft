from sqlalchemy import Column, Integer, String, Text, Float, JSON, ARRAY
from .database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    url = Column(Text)
    rating_count = Column(Text)
    cuisine_types = Column(JSON)  # or Text if it’s a string
    delivery_time = Column(Text)
    delivery_cost = Column(Text)
    min_order = Column(Text)
    header_image = Column(Text)
    avatar_image = Column(Text)
    rating_value = Column(Text)
    address = Column(Text)
    city_zip = Column(Text)