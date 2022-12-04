from pydantic import BaseModel, EmailStr
from typing import Optional


class Property(BaseModel):
    kamar_tidur: int
    kamar_mandi: int
    car_port: int
    luas_tanah: int
    luas_bangunan: int
    harga: int
    class Config :
        schema_extra = {
            "example": {
                "kamar_tidur": 8,
                "kamar_mandi": 4,
                "car_port": 2,
                "luas_tanah": 145,
                "luas_bangunan": 120,
                "harga": 270000000
            }
        }


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class ShowUser(BaseModel):
    name: str
    email: str

    class Config():
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
