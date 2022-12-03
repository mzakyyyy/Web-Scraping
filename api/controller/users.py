from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from fastapi import status, HTTPException
from auth.hash_password import Hash

def create(request: schemas.User, db: Session):
    new_user = models.User(
        name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user