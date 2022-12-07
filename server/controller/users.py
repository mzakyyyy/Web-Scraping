from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from fastapi import status, HTTPException
from auth.hash_password import Hash

def create(request: schemas.User, db: Session):
    new_user = models.User(
        name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    ada_user = db.query(models.User).filter(models.User.email == new_user.email).first()
    if ada_user:
        return {"Message": "Email already in use"}
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def retrieve_user(db: Session):
    user = db.query(models.User.email).all()
    return user