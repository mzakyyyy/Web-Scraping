from typing import Optional
from fastapi import APIRouter, Depends, status, Response, HTTPException
from schemas import schemas
from models import models
from config import database
from sqlalchemy.orm import Session
from sqlalchemy import and_
from controller import properties
from auth import OAuth2

router = APIRouter(
    tags=["Properties"]
)

get_db = database.get_db

@router.get('/property/all')
def get_all_properties(db: Session = Depends(get_db)):
    return properties.get_all(db)

@router.get('/property')
def get_filtered_properties(min_kamar_tidur: Optional[int], min_kamar_mandi: Optional[int], min_car_port: Optional[int], luas_tanah: Optional[int], luas_bangunan: Optional[int], minimal_harga: Optional[int], maksimal_harga: Optional[int], db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.get_all(min_kamar_tidur, min_kamar_mandi, min_car_port, luas_tanah, luas_bangunan, minimal_harga, maksimal_harga, db)


@router.post('/property', status_code=status.HTTP_201_CREATED)
def add_new_property(request: schemas.Property, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.create(request, db)


@router.delete('/property/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_property(id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.delete(id, db)


@router.get('/property/{id}')
def get_by_id(id: int, db: Session = Depends(get_db)):
    return properties.get_id(id, db)


@router.get('/kalkulator-kpr')
def get_cicilan(id: int, jangka_waktu: int, suku_bunga_fixed: float, masa_kredit_fix: int, suku_bunga_floating: float, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.cicilan_calculator(id, jangka_waktu, suku_bunga_fixed, masa_kredit_fix, suku_bunga_floating, db)


@router.get('/get-properties-kpr')
def get_properties_by_kpr(jangka_waktu: int, max_cicilan_awal: int, max_cicilan_akhir: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.kpr_properties(jangka_waktu, max_cicilan_awal, max_cicilan_akhir, db)

@router.get('/dariapi')
def get_dari_api():
    return properties.get_root()