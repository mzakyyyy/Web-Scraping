from fastapi import APIRouter, Depends, status, Response, HTTPException
from schemas import schemas
from config import database
from sqlalchemy.orm import Session
from controller import users


router = APIRouter(
    tags=["User"]
)

get_db = database.get_db


@router.post('/user', response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    return users.create(request, db)
