# -*- coding: utf-8 -*-
"""
Created on May 29 12:08:02 2021

@author: szszeghalmy

adat forrás: https://docs.google.com/spreadsheets/d/1ConGRVdv8jocW8G1lhpLqbDVnYwibjP1xhQJ5qiP_Ew/edit#gid=352892695


Megj.: Az adatokat eredetileg nem gépi felhasználásra szánták.A K-monitor tette át pdf-ből xlsx-be.
 Hibákat tartalmazhat és tartalmaz is. Pl. Debrecen 2x szerepelt.
"""

import os
import pandas

import folium as fl
import folium.plugins as flp
import branca.colormap as cm


import city2location as cl
from pandas.api.types import is_numeric_dtype

source_original = "data/covid19_elhunyt.xlsx"
source_with_city = "data/data_elhunyt.csv"

# source_original = "data/Egyéb_szoc_intézetek_COVID-19_tábla_megyék_2021.03.05_küldésre.xlsx"
# source_with_city = "data/data_egyeb_szoc_otth.csv"


headers = ['telepules', 'elhunytak', 'nepesseg', 'lats','longs']

def cleaning(df, header):
    if not is_numeric_dtype(df[header]):
        df[df[header].str.isnumeric() == False] = 0

    df[header] = df[header].astype(float)

def readData(file_name):
    df = pandas.read_csv(file_name, encoding='utf8', sep=";")

    cleaning(df, 'elhunytak')
    cleaning(df, 'nepesseg')
    cleaning(df, 'lats')
    cleaning(df, 'longs')

    # esetleges 0 letszamok javítása ... (megj. van ahol a másik mező is 0)
    mask = df['nepesseg'] == 0
    df.loc[mask, 'nepesseg'] = 1000

    return df

def str_elhunyt(row):
    ndeath = int(row['elhunytak'])
    population = max(int(row['nepesseg']), 1)
    city = row['telepules']

    return f"<b>{city}</b>" \
    f" elhunyt: {ndeath} fő<br>" \
    f" népesség: {population} fő<br>" \
    f" elhunytak/népesség: {ndeath/population*100:0.2f}% "



def createMap(df): # dataframe

    df_ratio = df['elhunytak']/df['nepesseg']
    maxCasesR = df_ratio.max()
    maxCases = df['elhunytak'].max()


    map = fl.Map(location=[47.20, 19.50], tiles='cartodbpositron', zoom_start=8)
    colormap = cm.LinearColormap(colors=['green', 'lightgreen', 'yellow', 'orange' , 'red', 'black'],
                                 vmin=0, vmax=maxCasesR*100)

    colormap.add_to(map)

    scale_factor_circle = 10000.0/maxCases # 5000 - max radius of city (in metre

    for i in range(df.shape[0]):
        row = df.iloc[i]

        fl.Circle(
            location = [row['lats'], row['longs']],
            tooltip = str_elhunyt(row),
            radius = min(max(1000,  row['elhunytak']* scale_factor_circle), 10000),
            color = colormap(df_ratio.iloc[i]*100),
            # radius = max(1,  df_ratio.iloc[i]* scale_factor_circle),
            # color = color,
            opacity = 0.75,
            fill = True

        ).add_to( map )

    return map


html_template = """ 
<h3>{title} </h3>
<br>
<p>{message}</p><br>
<p><i>{note}</i></p>
"""

def createHtml(map, title, message, note, dest_filename = 'map.html'):

    html = html_template.format(title=title, message=message, note=note)

    map.get_root().html.add_child(fl.Element(html))
    map.save(dest_filename)




title = "COVID19 - elhunytak száma településenként (2021.03.04-ig)"
message ="""Az adatok forrása: https://docs.google.com/spreadsheets/d/1ConGRVdv8jocW8G1lhpLqbDVnYwibjP1xhQJ5qiP_Ew/edit#gid=352892695"""
note = """Megj.: A térkép a <a href="https://python-visualization.github.io/folium/">Folium csomag</a> használatára ad példát. Nem célja tájékoztatást adni az aktuális vírushelyzetről és erre a felhasznált adatok nem is alkalmasak.</i>"""


if __name__ == '__main__':
    if not os.path.exists(source_with_city):
        cl.extendWithCoord(source_original, source_with_city)

    data = readData(source_with_city)
    map = createMap(data)

    createHtml(map, title, message, note, 'covid_elhunyt.html')
