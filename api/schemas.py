from pydantic import BaseModel

class Property(BaseModel):
    kamar_tidur: int
    kamar_mandi: int
    car_port: int
    luas_tanah: int
    luas_bangunan: int
    harga: int

class User(BaseModel):
    name: str
    email: str
    password: str

class ShowUser(BaseModel):
    name: str
    email: str
    class Config():
        orm_mode = True