# -*- coding: utf-8 -*-
"""
Created on Marc 19 21:17:45 2021

@author: szszeghalmy

adat forrás: https://drive.google.com/drive/folders/1yitS_a8PhZ30KREQN_iuoVjVaA-j7KZG?fbclid=IwAR3JFgtNEmEXbNmg-zk2fZ2v86LnZ1Si0Gxly7qUj08Ym7an33xiGUQDvSY

Megj.: Az adatokat nem gépi felhasználásra szánták.
 -- A városnevekben, címekben előforduló hibák nem kerültek javításra. Amennyiben az OSM adatbázisában
    a teljes cím nem volt fellelhető, az irányítószám alapján került a jelölő létrehozásra.
 -- Esztergom;Idősek Otthona: 63 (71) mezőből a 63-as értéket őriztem meg.
"""

import os
import pandas

import folium as fl
import folium.plugins as flp
import branca.colormap as cm


import city2location as cl

source_original = "data/Szoc_otthonok_COVID-19_tábla_megyék_21.03.05_küldésre.xlsx"
source_with_city = "data/data_szoc_otth.csv"

# headers = ['sorszam', 'megye', 'jaras_v_kerulet', 'intezmeny_nev', 'cim', 'dolgozo_letszam', 'ferohely', 'cpoz_dolgozo_szam', 'cpoz_gondozott_szam', 'cpoz_dolgozo_korhazi_ellatas', 'cpoz_gondozott_korhazi_ellatas', 'cpoz_dolgozo_elhunyt', 'cpoz_gondozott_elhunyt', 'cpoz_dolgozo_gyogyult', 'cpoz_gondozott_gyogyult', 'lats','longs']


def readData(file_name):
    df = pandas.read_csv(file_name, encoding='utf8', sep=";")

    # esetleges 0 letszamok javítása ... (megj. van ahol a másik mező is 0)
    mask = df['ferohely'] == 0
    df.loc[mask, 'ferohely'] = df.loc[mask, 'cpoz_gondozott_szam']

    mask = df['dolgozo_letszam'] == 0
    df.loc[mask, 'dolgozo_letszam'] = df.loc[mask, 'cpoz_dolgozo_szam']

    return df

def str_intezmeny(row):
    return f"<b>{row['intezmeny_nev']}</b><br>" \
    f"ferőhely: {int(row['ferohely'])}<br>"

def str_gondozottak(row):
    n = max(int(row['ferohely']), 1)
    ncase = int(row['cpoz_gondozott_szam'])
    nhosp = int(row['cpoz_gondozott_korhazi_ellatas'])
    ndeath = int(row['cpoz_gondozott_elhunyt'])
    nrecov = int(row["cpoz_gondozott_gyogyult"])

    return f"{str_intezmeny(row)}" \
    f"<br><b>Covid19 pozitív gondozottak:</b><br>" \
    f" esetszám: {ncase} ({ncase/n*100:0.2f}%)<br>" \
    f" kórházi ellátás: {nhosp} ({nhosp/n*100:0.2f}%)<br>" \
    f" elhunyt: {ndeath} ({ndeath/n*100:0.2f}%)<br>" \
    f" gyógyult: {nrecov} ({nrecov/n*100:0.2f}%)<br>"


def str_dolgozok(row):
    n = max(int(row['dolgozo_letszam']), 0)
    ncase = int(row['cpoz_dolgozo_szam'])
    nhosp = int(row['cpoz_dolgozo_korhazi_ellatas'])
    ndeath = int(row["cpoz_dolgozo_elhunyt"])
    nrecov = int(row["cpoz_dolgozo_gyogyult"])

    return f"{str_intezmeny(row)}" \
    f" dolgozók száma: {row['dolgozo_letszam']}<br>" \
    f"<br><b>Covid19 pozitív dolgozók:</b><br>" \
    f" esetszám: {ncase} ({ncase/n*100:0.2f}%)<br>" \
    f" kórházi ellátás: {nhosp} ({nhosp/n*100:0.2f}%)<br>" \
    f" elhunyt: {ndeath} ({ndeath/n*100:0.2f}%)<br>" \
    f" gyógyult: {nrecov} ({nrecov/n*100:0.2f}%)<br>"




def createLayer(df, layerName, header_value, header_base, tooltip_func):
    layer = fl.FeatureGroup(name=layerName, overlay=False, control=True)

    df_ratio = df[header_value]/df[header_base]

    maxCases = df_ratio.max()

    # vmax = maxCase*100 lenne ideális esetben, de egy színkód lesz az összes adathoz
    colormap = cm.LinearColormap(colors=['yellow', 'green', 'blue', 'purple', 'red'], vmin=0, vmax=100)


    # különböző koordináták
    unique_locs = df[['lats', 'longs']].drop_duplicates()

    marker_cluster = flp.MarkerCluster(
        name='SzocInt',
        overlay=True,
        control=False,
        icon_create_function=None
    )

    # koordináták szerint rakjuk ki a markereket, mert az egy helyre esoket
    # így lehet majd láthatóvá tenni (mint a google térképnél)
    for idx, loc in enumerate(zip(unique_locs['lats'], unique_locs['longs'])):
        if loc[0] < 0.001:
            continue

        # az azonos térképi koordinátára eső sorok
        mask = (df['lats'] == loc[0]) & (df['longs']==loc[1])

        df_part = df[mask]
        df_ratio_part = df_ratio[mask]

        for i in range(df_part.shape[0]):

            row = df_part.iloc[i]
            # 0 férőhelyszámnál/dolgozószámnál szürkével jelöli meg
            color = "#808080ff" if pandas.isnull(df_ratio_part.iloc[i]) \
              else colormap(df_ratio_part.iloc[i]*100)

            fl.Marker(
              location = [row['lats'], row['longs']],
              tooltip = tooltip_func(row),
              icon = fl.Icon(color='black', icon_color=color)
            ).add_to( layer if df_part.shape[0] == 1 else marker_cluster )

    marker_cluster.add_to(layer)

    return layer

def createMap(df): # dataframe
    map = fl.Map(location=[47.20, 19.50], zoom_start=8)

    colormap = cm.LinearColormap(colors=['yellow', 'green', 'blue', 'purple', 'red'], vmin=0, vmax=100)
    colormap.add_to(map)

    base_map = fl.FeatureGroup(name='Alaptérkép', overlay=True, control=False, show=False)
    fl.TileLayer(tiles='cartodbpositron').add_to(base_map)
    base_map.add_to(map)

    layer1 = createLayer(df, 'Covid pozitív gondozott/férőhely', 'cpoz_gondozott_szam', 'ferohely',
                         str_gondozottak)
    layer1.add_to(map)
    #
    layer2 = createLayer(df, 'Elhunyt covid pozitív gondozott/férőhely', 'cpoz_gondozott_elhunyt', 'ferohely',
                         str_gondozottak)
    layer2.add_to(map)
    #
    layer3 = createLayer(df, 'Covid pozitív dolgozó/dolgozó létszám', 'cpoz_dolgozo_szam', 'dolgozo_letszam',
                         str_dolgozok)
    layer3.add_to(map)
    #
    layer4 = createLayer(df, 'Elhunyt covid pozitív dolgozó/dolgozó létszám', 'cpoz_dolgozo_elhunyt', 'dolgozo_letszam', str_dolgozok)
    layer4.add_to(map)

    fl.map.LayerControl(collapsed=False).add_to(map)


    return map


def createHtml(map, title_html, dest_filename = 'map.html'):

    map.get_root().html.add_child(fl.Element(title_html))
    map.save(dest_filename)

# a javascript megoldja, hogy ne az alaptérkép legyen megjeleítve az elején, hanem
# az egyik jelölőket tartalmazó réteg
title_html_gondozott = """

<script>
$(document).ready(
    function () {
		x = $("input[type='radio']");
		x[1].click();
    }
);
</script>

<h3>COVID19 a szociális- és idősotthonokban (2021.03.05-ig) </h3>
                    
<p>Az adatok forrása: <a href="https://drive.google.com/drive/folders/1yitS_a8PhZ30KREQN_iuoVjVaA-j7KZG?fbclid=IwAR3JFgtNEmEXbNmg-zk2fZ2v86LnZ1Si0Gxly7qUj08Ym7an33xiGUQDvSY">Szoc_otthonok_COVID-19_tábla_megyék_21.03.05_küldésre.xlsx</a><br></p>
<br><i>Megj.: Megjegyzés: A térkép a <a href="https://python-visualization.github.io/folium/">Folium csomag</a> használatára ad példát. Nem célja tájékoztatást adni az aktuális vírushelyzetről és erre a felhasznált adatok nem is alkalmasak.</i>"""


if __name__ == '__main__':
    if not os.path.exists(source_with_city):
        cl.extendWithCoord(source_original, source_with_city)

    data = readData(source_with_city)
    map = createMap(data)

    createHtml(map, title_html_gondozott, 'szoc_gondozott.html')

