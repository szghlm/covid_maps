# -*- coding: utf-8 -*-
"""
Created on Marc 3 15:12:32 2021

@author: szszeghalmy
"""

import enum
import geopy
import pandas

from geopy.extra.rate_limiter import RateLimiter

import logging
logging.basicConfig(filename='info2.log', encoding='utf-8', level=logging.INFO)


headers = ['sorszam', 'megye', 'jaras_v_kerulet', 'intezmeny_nev', 'cim', 'dolgozo_letszam', 'ferohely', 'cpoz_dolgozo_szam', 'cpoz_gondozott_szam', 'cpoz_dolgozo_korhazi_ellatas', 'cpoz_gondozott_korhazi_ellatas', 'cpoz_dolgozo_elhunyt', 'cpoz_gondozott_elhunyt', 'cpoz_dolgozo_gyogyult', 'cpoz_gondozott_gyogyult']

# original_headers = ['Sorszám', 'Megye', 'Járás/kerület ', 'Szociális / Idős otthon neve', 'Címe (irányítószám, település, utca, házszám)', 'Dolgozói létszám (intézmény összes dolgozója)', 'Intézményi férőhelyek száma', 'COVID-19 pozitív dolgozók száma', 'COVID-19 pozitív gondozottak száma', 'COVID-19 pozitív dolgozók kórházi ellátása ', 'COVID-19 pozitív gondozott kórházi ellátása', 'Elhunyt COVID-19 pozitív dolgozók száma', 'Elhunyt COVID-19 pozitív gondozottak  száma', 'Gyógyult COVID-19 pozitív dolgozók száma', 'Gyógyult COVID-19 pozitív gondozottak száma száma']


# for test
__source = "data/Szoc_otthonok_COVID-19_tábla_megyék_21.03.05_küldésre.xlsx"
__dest = "data/data_szoc_otth.csv"

class LocLevel(enum.Enum):
    PRECISE = 0
    POSTCODE = 1
    UNKNOWN = -1
    NOMINATIM_ERR = -2

def __getLocation(address):
    locator = geopy.geocoders.Nominatim(user_agent="city2location2", timeout=7)

    # sok lekérdezés lesz, tartjuk a szolgáltató által elvárt ütemet
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

    ret = [0, 0], LocLevel.UNKNOWN

    # a teljes cím alapján történő kezelés
    location = locator.geocode(address)
    if location is not None:
        ret = [location.latitude, location.longitude], LocLevel.PRECISE

    # irányítószám alapján történő keresés
    else:
        postcode = address[0:4] + " Hungary"
        location = locator.geocode(postcode)
        if location is not None:
            ret = [location.latitude, location.longitude], LocLevel.POSTCODE

    return ret


def __readCovidData(file_name):

    datalst = []

    # Az xlsx fájl lapjainak bejárása (0. lap az összesített, az 1-20 tartalmazza az adatokat (megyénként)
    for i in range(1, 21):
        # lap felolvasása és üres oszlopok kiszedése
        d = pandas.read_excel(file_name, i).iloc[0:, 0:15]

        # könnyebben használható fejlécek beállítása
        d.columns = headers

        # összesítő sor és az esetleges alatta lévő sorok törlése
        last_idx = int(d["sorszam"].max())
        print(last_idx)
        d = d.iloc[0:last_idx, :]

        # egy megye adatának hozzáadása a listához
        datalst.append( d )

    # az összes szükséges adat
    return pandas.concat(datalst)


def __addLocations(df): # dataFrame
    """
    Dataframe kiegészítése a koordinátákat és azok megbízhatóságát tartalmazó oszlopokkal. (lats, longs, location_levels)
    
    Az átalakítás során történő hibák az info2.log fájlban. 
    """
    addresses = df['cim']
    lats = []
    longs = []
    location_levels = []
    for add in addresses:
        try:
            loc, level = __getLocation(add)
            logging.info(f"{level.name} {add}")
            lats.append(loc[0])
            longs.append(loc[1])
            location_levels.append(level)
            if level == LocLevel.UNKNOWN:
                logging.warning(f"{level.name} {add}")
        except:
            lats.append(0)
            longs.append(0)
            location_levels.append(LocLevel.NOMINATIM_ERR)
            logging.warning(f"{LocLevel.NOMINATIM_ERR} {add}")


    df["lats"] = lats
    df["longs"] = longs
    df["location_levels"] = location_levels
    return df


def extendWithCoord(source_filename = __source, dest_filename = __dest):
    df = __readCovidData(source_filename)
    df = __addLocations(df)
    df.to_csv(dest_filename, encoding="utf-8", sep=";", index=False)


if __name__ ==  "__main__":
    extendWithCoord(__source, __dest)

