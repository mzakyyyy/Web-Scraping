from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from sqlalchemy import and_
from fastapi import status, HTTPException
import requests
from enum import Enum
import pickle
import json
import numpy as np


class BankName(str, Enum):
    bca = "BCA"
    mandiri = "Mandiri"
    btn = "BTN"

global model
with open('./controller/house_price_prediction.pickle', 'rb') as f:
    model = pickle.load(f)

global data_columns
with open('./controller/house_columns.json', 'r') as f:
    data_columns = json.load(f)['data_columns']
    kota = data_columns[5:]

def get_estimated_car_price(kota, kamar_tidur, kamar_mandi, car_port, luas_tanah, luas_bangunan): 
    try:
        kota_index = data_columns.index(kota.title())
    except:
        perusahaan_index = -1
        
    x = np.zeros(len(data_columns))
    x[0] = kamar_tidur
    x[1] = kamar_mandi
    x[2] = car_port
    x[3] = luas_tanah
    x[4] = luas_bangunan
    
    if kota_index >= 0:
        x[kota_index] = 1
        return round(np.exp(model.predict([x])[0]))
    
    return "Data lokasi tidak ditemukan"


def get_all(min_kamar_tidur: int, min_kamar_mandi: int, min_car_port: int, luas_tanah: int, luas_bangunan: int, minimal_harga: int, maksimal_harga: int, db: Session):
    properties = db.query(models.Property).filter(and_(models.Property.kamar_tidur >= min_kamar_tidur,
                                                       models.Property.kamar_mandi >= min_kamar_mandi,
                                                       models.Property.car_port >= min_car_port,
                                                       models.Property.luas_tanah >= luas_tanah,
                                                       models.Property.luas_bangunan >= luas_bangunan,
                                                       models.Property.harga >= minimal_harga,
                                                       models.Property.harga <= maksimal_harga)).all()
    if not properties:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Tidak ada properti yang memenuhi spesifikasi")
    return {f"Terdapat {len(properties)} properti yang memenuhi kriteria": properties}


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


def calculator(harga: int, jangka_waktu: int, suku_bunga_fixed: float, masa_kredit_fix: int, suku_bunga_floating: float):
    cicilan_pokok = harga/(jangka_waktu*12)
    bunga_per_bulan = (harga * (suku_bunga_fixed/100))/12
    cicilan_total = bunga_per_bulan + cicilan_pokok
    cicilan_terbayar = cicilan_total*12*masa_kredit_fix

    sisa_cicilan = harga - cicilan_terbayar
    bunga_sisa_per_bulan = (sisa_cicilan*(suku_bunga_floating/100))/12
    cicilan_sisa_total = cicilan_pokok + bunga_sisa_per_bulan

    cicilan = [round(cicilan_total), round(cicilan_sisa_total)]
    total = (cicilan[0]*12*masa_kredit_fix)+(cicilan[1]*12*(jangka_waktu-masa_kredit_fix))
    total = "{:,}".format(total)
    total = total.replace(",", ".")

    harga = "{:,}".format(harga)
    harga = harga.replace(",", ".")
    for i in range(len(cicilan)):
        cicilan[i] = "{:,}".format(cicilan[i])
        cicilan[i] = str(cicilan[i]).replace(',', '.')
    return {
        "Informasi Pinjaman Anda": {
            "Harga Jual Properti": f'Rp {harga}',
            "Tenor": f'{jangka_waktu} tahun',
        },
        "Angsuran Termin 1": {
            "Masa Kredit Termin 1": f'{masa_kredit_fix} tahun',
            "Suku Bunga Termin 1": f'{suku_bunga_fixed} %',
            "Cicilan per Bulan Termin 1": f'Rp {cicilan[0]}'
        },
        "Angsuran Termin 2": {
            "Masa Kredit Termin 2": f'{jangka_waktu-masa_kredit_fix} tahun',
            "Suku Bunga Termin 2": f'{suku_bunga_floating} %',
            "Cicilan per Bulan Termin 2": f'Rp {cicilan[1]}'
        },
        "Jumlah uang yang harus Anda keluarkan": f'Rp {total}'
    }
    return cicilan


def cicilan_calculator_bank(harga: int, bank: BankName, jangka_waktu: int, suku_bunga_floating: float):
    cicilan = []
    if bank is BankName.bca:
        suku_bunga_fixed = 9
        masa_kredit_fix = 3
    elif bank is BankName.mandiri:
        suku_bunga_fixed = 4.88
        masa_kredit_fix = 5
    elif bank is BankName.btn:
        suku_bunga_fixed = 3.72
        masa_kredit_fix = 1
    
    cicilan_pokok = harga/(jangka_waktu*12)
    bunga_per_bulan = (harga * (suku_bunga_fixed/100))/12
    cicilan_total = bunga_per_bulan + cicilan_pokok
    cicilan_terbayar = cicilan_total*12*masa_kredit_fix

    sisa_cicilan = harga - cicilan_terbayar
    bunga_sisa_per_bulan = (sisa_cicilan*(suku_bunga_floating/100))/12
    cicilan_sisa_total = cicilan_pokok + bunga_sisa_per_bulan

    cicilan = [round(cicilan_total), round(cicilan_sisa_total)]
    total = (cicilan[0]*12*masa_kredit_fix)+(cicilan[1]*12*(jangka_waktu-masa_kredit_fix))
    total = "{:,}".format(total)
    total = total.replace(",", ".")

    harga = "{:,}".format(harga)
    harga = harga.replace(",", ".")
    for i in range(len(cicilan)):
        cicilan[i] = "{:,}".format(cicilan[i])
        cicilan[i] = str(cicilan[i]).replace(',', '.')
    return {
        "Bank Penyedia": bank.value,
        "Informasi Pinjaman Anda": {
            "Harga Jual Properti": f'Rp {harga}',
            "Tenor": f'{jangka_waktu} tahun',
        },
        "Angsuran Termin 1": {
            "Masa Kredit Termin 1": f'{masa_kredit_fix} tahun',
            "Suku Bunga Termin 1": f'{suku_bunga_fixed} %',
            "Cicilan per Bulan Termin 1": f'Rp {cicilan[0]}'
        },
        "Angsuran Termin 2": {
            "Masa Kredit Termin 2": f'{jangka_waktu-masa_kredit_fix} tahun',
            "Suku Bunga Termin 2": f'{suku_bunga_floating} %',
            "Cicilan per Bulan Termin 2": f'Rp {cicilan[1]}'
        },
        "Jumlah uang yang harus Anda keluarkan": f'Rp {total}'
    }

def kpr_properties(jangka_waktu: int, max_cicilan_awal: int, max_cicilan_akhir: int, db: Session):
    properties = showall(db)
    suku_bunga_fixed = 5
    masa_kredit_fix = 5
    suku_bunga_floating = 7.5
    list_properties = []
    for properti in properties:
        cicilan_pokok = properti.harga/(jangka_waktu*12)
        bunga_per_bulan = (properti.harga * (suku_bunga_fixed/100))/12
        cicilan_total = bunga_per_bulan + cicilan_pokok
        cicilan_terbayar = cicilan_total*12*masa_kredit_fix

        sisa_cicilan = properti.harga - cicilan_terbayar
        bunga_sisa_per_bulan = (sisa_cicilan*(suku_bunga_floating/100))/12
        cicilan_sisa_total = cicilan_pokok + bunga_sisa_per_bulan

        cicilan = [round(cicilan_total), round(cicilan_sisa_total)]
        if ((cicilan[0] <= max_cicilan_awal) & (cicilan[1] <= max_cicilan_akhir)):
            list_properties.append(properti)
        else:
            pass
    return (f"Ada {len(list_properties)} properti yang memenuhi keinginan Anda: ", list_properties)


def compare_price(id: int, db: Session):
    prop = get_id(id, db)
    harga_predict = prediction(id, db)
    harga_predict = harga_predict.split(" ")
    harga_predict = harga_predict[-1]
    harga_predict = int(harga_predict.replace(".", ""))
    
    if (int(prop.harga) < harga_predict):
        return ("Harga jual properti ini berada di bawah standard. Ayo cepat beli!")
    else:
        return ("Harga properti ini lebih mahal dari perkiraan. Pikir-pikir dulu deh!")

def get_from_test():
    url = 'https://tst-price-prediction.azurewebsites.net/login?'
    data = {"username": "jaki", "password": "jaki"}
    response = requests.post(url, data=data)
    jsonresponse = response.json()
    bearertoken = str(jsonresponse['access_token'])
    return bearertoken
