from typing import Optional
from fastapi import APIRouter, Depends, status, Response, HTTPException
from schemas import schemas
from models import models
from config import database
from sqlalchemy.orm import Session
from sqlalchemy import and_
from controller import properties
from auth import OAuth2

router = APIRouter()

get_db = database.get_db


@router.get('/property/all', tags=["Property"])
def get_all(db: Session = Depends(get_db)):
    return properties.showall(db)


@router.get('/property', tags=["Property"])
def get_filtered_properties(min_kamar_tidur: Optional[int] = 0, min_kamar_mandi: Optional[int] = 0, min_car_port: Optional[int] = 0, luas_tanah: Optional[int] = 0, luas_bangunan: Optional[int] = 0, minimal_harga: Optional[int] = 0, maksimal_harga: Optional[int] = 999999999999, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.get_all(min_kamar_tidur, min_kamar_mandi, min_car_port, luas_tanah, luas_bangunan, minimal_harga, maksimal_harga, db)


@router.post('/property', status_code=status.HTTP_201_CREATED, tags=["Property"])
def add_new_property(request: schemas.Property, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.create(request, db)


@router.delete('/property/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=["Property"])
def delete_property(id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(OAuth2.get_current_user)):
    return properties.delete(id, db)


@router.get('/property/{id}', tags=["Property"])
def get_by_id(id: int, db: Session = Depends(get_db)):
    return properties.get_id(id, db)


@router.get('/kpr/property/{id}', tags=["KPR Calculator"])
def kpr_property_calculator(id: int, jangka_waktu: int, suku_bunga_fixed: float, masa_kredit_fix: int, suku_bunga_floating: float, db: Session = Depends(get_db)):
    prop = db.query(models.Property).filter(
        models.Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Properti dengan id {id} tidak ada")
    harga = prop.harga
    cicilan = properties.calculator(
        harga, jangka_waktu, suku_bunga_fixed, masa_kredit_fix, suku_bunga_floating)
    for i in range(len(cicilan)):
        cicilan[i] = "{:,}".format(cicilan[i])
        cicilan[i] = str(cicilan[i]).replace(',', '.')
    return {f'Cicilan Anda dalam {masa_kredit_fix} tahun pertama': f'Rp {cicilan[0]} per bulan',
            f'{jangka_waktu-masa_kredit_fix} tahun selanjutnya': f'Rp {cicilan[1]} per bulan'}


@router.get('/kpr', tags=["KPR Calculator"])
def kpr_calculator(harga: int, jangka_waktu: int, suku_bunga_fixed: float, masa_kredit_fix: int, suku_bunga_floating: float):
    cicilan = properties.calculator(
        harga, jangka_waktu, suku_bunga_fixed, masa_kredit_fix, suku_bunga_floating)
    for i in range(len(cicilan)):
        cicilan[i] = "{:,}".format(cicilan[i])
    return (f"Cicilan Anda dalam {masa_kredit_fix} tahun pertama: Rp {str(cicilan[0]).replace(',', '.')} per bulan dan {jangka_waktu-masa_kredit_fix} tahun selanjutnya: Rp {str(cicilan[1]).replace(',', '.')} per bulan")


@router.get('/kpr/property/{id}/bank/{bank}', tags=["KPR Calculator with Bank Policy"])
def kpr_property_bank_calculator(id: int, bank: properties.BankName, jangka_waktu: int, suku_bunga_floating: float, db: Session = Depends(get_db)):
    prop = db.query(models.Property).filter(
        models.Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Properti dengan id {id} tidak ada")
    harga = prop.harga
    return properties.cicilan_calculator_bank(harga, bank, jangka_waktu, suku_bunga_floating)


@router.get('/kpr/bank/{bank}', tags=["KPR Calculator with Bank Policy"])
def kpr_bank_calculator(harga: int, bank: properties.BankName, jangka_waktu: int, suku_bunga_floating: int):
    return properties.cicilan_calculator_bank(harga, bank, jangka_waktu, suku_bunga_floating)


@router.get('/get-properties-kpr', tags=["Other"])
def get_properties_by_kpr(jangka_waktu: int, max_cicilan_awal: int, max_cicilan_akhir: int, db: Session = Depends(get_db)):
    return properties.kpr_properties(jangka_waktu, max_cicilan_awal, max_cicilan_akhir, db)


@router.get('/predict', tags=["Prediction"])
def get_prediction(kota: str, kamar_tidur: int, kamar_mandi: int, car_port: int, luas_tanah: int, luas_bangunan: int):
    try:
        results = properties.get_estimated_car_price(
            kota, kamar_tidur, kamar_mandi, car_port, luas_tanah, luas_bangunan)
        results = "{:,}".format(results)
        results = results.replace(",", ".")

        return (f'Properti ini diprediksi berada di harga: Rp{results}')
    except:
        return "Data lokasi tidak ditemukan"


# @router.get('/compare', tags=["Prediction"])
# def compare(id: int, db: Session = Depends(get_db)):
#     return properties.compare_price(id, db)
