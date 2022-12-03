from fastapi import APIRouter, Depends, HTTPException, status
from schemas import schemas
from models import models
from config import database
from sqlalchemy.orm import Session
from auth.hash_password import Hash

router = APIRouter(
    tags=["Authentication"]
)


@router.post('/login')
def login(request: schemas.Login, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")
    if not Hash.verify(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")
    return user
