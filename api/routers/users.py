from typing import Optional
from fastapi import APIRouter, Depends, status, Response, HTTPException
import schemas, models, database
from sqlalchemy.orm import Session
from sqlalchemy import and_
from hash_password import Hash

router = APIRouter()

@router.post('/user', response_model=schemas.ShowUser, tags=["User"])
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):
    new_user = models.User(
        name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
