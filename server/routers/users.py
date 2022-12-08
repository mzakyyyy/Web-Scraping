from fastapi import APIRouter, Depends, status, Response, HTTPException
from schemas import schemas
from config import database
from sqlalchemy.orm import Session
from controller import users
from auth import OAuth2


router = APIRouter(
    tags=["User"]
)

get_db = database.get_db


@router.post('/user')
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    return users.create(request, db)

@router.delete('/user/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return users.delete(id, db)

@router.get('/user')
def show_user(db: Session = Depends(get_db)):
    return users.retrieve_user(db)