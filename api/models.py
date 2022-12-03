from sqlalchemy import Column, Integer, String
from database import Base

class Property(Base):
    __tablename__ = 'properties'
    id = Column(Integer, primary_key=True, index=True)
    kamar_tidur = Column(Integer)
    kamar_mandi = Column(Integer)
    car_port = Column(Integer)
    luas_tanah = Column(Integer)
    luas_bangunan = Column(Integer)
    harga = Column(Integer)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)