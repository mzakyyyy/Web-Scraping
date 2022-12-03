from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from sqlalchemy import and_
from fastapi import status, HTTPException


def get_all(min_kamar_tidur: int, min_kamar_mandi: int, min_car_port: int, db: Session):
    properties = db.query(models.Property).filter(and_(models.Property.kamar_tidur >= min_kamar_tidur,
                                                       models.Property.kamar_mandi >= min_kamar_mandi,
                                                       models.Property.car_port >= min_car_port)).all()
    if not properties:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Tidak ada properti yang memenuhi spesifikasi")
    return properties


def create(request: schemas.Property, db: Session):
    new_property = models.Property(kamar_tidur=request.kamar_tidur, kamar_mandi=request.kamar_mandi,
                                   car_port=request.car_port, luas_tanah=request.luas_tanah, luas_bangunan=request.luas_bangunan, harga=request.harga)
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


def delete(id: int, db: Session):
    properties = db.query(models.Property).filter(models.Property.id == id)
    if not properties.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Properti dengan id {id} tidak ada")
    properties.delete(synchronize_session=False)
    db.commit()
    return {"Message": f"Properti dengan id {id} telah dihapus"}


def get_id(id: int, db: Session):
    properties = db.query(models.Property).filter(
        models.Property.id == id).first()
    if not properties:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Properti dengan id {id} tidak ada")
    return properties


def showall(db: Session):
    properties = db.query(models.Property).all()
    return properties


def provide_cicilan(id: int, jangka_waktu: int, suku_bunga_fixed: float, masa_kredit_fix: int, suku_bunga_floating: float, db: Session):
    properties = db.query(models.Property).filter(
        models.Property.id == id).first()
    if not properties:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Properti dengan id {id} tidak ada")
    cicilan_pokok = properties.harga/(jangka_waktu*12)
    bunga_per_bulan = (properties.harga * (suku_bunga_fixed/100))/12
    cicilan_total = bunga_per_bulan + cicilan_pokok
    cicilan_terbayar = cicilan_total*12*masa_kredit_fix

    sisa_cicilan = properties.harga - cicilan_terbayar
    bunga_sisa_per_bulan = (sisa_cicilan*(suku_bunga_floating/100))/12
    cicilan_sisa_total = cicilan_pokok + bunga_sisa_per_bulan

    cicilan_list = [cicilan_total, cicilan_sisa_total]

    return cicilan_list


def cicilan_calculator(id: int, jangka_waktu: int, suku_bunga_fixed: float, masa_kredit_fix: int, suku_bunga_floating: float, db: Session):
    properties = db.query(models.Property).filter(
        models.Property.id == id).first()
    if not properties:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Properti dengan id {id} tidak ada")
    cicilan_pokok = properties.harga/(jangka_waktu*12)
    bunga_per_bulan = (properties.harga * (suku_bunga_fixed/100))/12
    cicilan_total = bunga_per_bulan + cicilan_pokok
    cicilan_terbayar = cicilan_total*12*masa_kredit_fix

    sisa_cicilan = properties.harga - cicilan_terbayar
    bunga_sisa_per_bulan = (sisa_cicilan*(suku_bunga_floating/100))/12
    cicilan_sisa_total = cicilan_pokok + bunga_sisa_per_bulan

    return {
        f"Cicilan {masa_kredit_fix} tahun pertama": f"{cicilan_total} per bulan",
        "Cicilan sisa": f"{cicilan_sisa_total} per bulan"
    }


def kpr_properties(jangka_waktu: int, max_cicilan_awal: int, max_cicilan_akhir: int, db: Session):
    properties = showall(db)
    suku_bunga_fixed = 5
    masa_kredit_fix = 5
    suku_bunga_floating = 7.5
    list_properties = []
    for properti in properties:
        cicilan_func = provide_cicilan(
            properti.id, jangka_waktu, suku_bunga_fixed, masa_kredit_fix, suku_bunga_floating, db)
        if ((cicilan_func[0] <= max_cicilan_awal) & (cicilan_func[1] <= max_cicilan_akhir)):
            list_properties.append(properti)
        else:
            pass
    return list_properties
