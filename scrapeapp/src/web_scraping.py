import os
from csv import writer
import json
import requests
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}


def extract_luas(luas):
    # Extract luas without unit
    luas_extracted = luas.split(' ')
    return (int(luas_extracted[0]))


def extract_harga(harga):
    # Extract harga without miliar and juta
    if (harga.__contains__('Miliar')):
        harga = int(float(harga.split(' ')[1])*10**9)
    else:
        harga = int(float(harga.split(' ')[1])*10**6)
    return harga


def scrape(object):
    id = 1
    for page in range(21, 101):
        print("Sedang melakukan scraping halaman-"+str(page))
        url = f'https://www.rumah123.com/jual/residensial/?bedroom=1&bathroom=1&minBuiltupSize=1&page={page}#qid~0c306a83-00e9-4b15-9b22-dc820d9b9ba6'
        pages = requests.get(url, headers=headers)
        soup = BeautifulSoup(pages.text, 'html.parser')

        properties = soup.find_all("div", {'data-test-id': 'card-premier'})
        
        for property in properties:
            prop_att = property.find("div", "ui-organisms-card-r123-featured__middle-section__attribute")
            alamat = property.find('p', 'ui-organisms-card-r123-featured__middle-section__address').text.strip()
            kota = alamat.split(", ")[1]
            # Kamar and Car Port
            attributes = ([kamar.text for kamar in prop_att.find_all(class_="relative ui-molecules-list__item")])
            kamar_tidur = int(attributes[0])
            kamar_mandi = int(attributes[1])
            try:
                car_port = int(attributes[2])
            except IndexError:
                pass

            # Luas
            att_info = ([luas.text for luas in property.find_all("span", "attribute-value")])
            luas_tanah = att_info[0]
            luas_tanah = extract_luas(luas_tanah)
            try:
                luas_bangunan = att_info[1]
                luas_bangunan = extract_luas(luas_bangunan)
            except IndexError:
                pass

            # Harga
            harga = property.strong.text.strip()
            harga = harga.replace(',', '.')
            harga = extract_harga(harga)

            result = {
                "id": id,
                "kota": kota,
                "kamar_tidur": kamar_tidur,
                "kamar_mandi": kamar_mandi,
                "car_port": car_port,
                "luas_tanah": luas_tanah,
                "luas_bangunan": luas_bangunan,
                "harga": harga
            }

            object.append(result)
            id += 1

def main():
    filename = input("Nama file: ")
    records = []
    scrape(records)

    filepath = 'D:\Data Zaky\Semester 5\Tugas Besar\Web Scraping\scrapeapp\data'
    dump = json.dumps(records, indent=4)
    filepath = os.path.join(filepath, filename + ".json")
    with open(filepath, "w") as file:
        file.write(dump)
        file.close()

main()
