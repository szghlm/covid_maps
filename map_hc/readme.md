<h3> COVID19 adatok térképi megjelenítése </h3>

Az elkészült térkép a [Folium csomag]("https://python-visualization.github.io/folium/") használatára ad példát. Nem célja tájékoztatást adni a vírushelyzetről.

### Covid19 adatok

A magyarországi szociális/idős otthonok 2021.03.05-ig összesített fertőzöttségi, halálozási és gyógyulási adatai intézményenkénti bontásban. 
A térkép nem tartalmazza az egyéb intézményekre vonatkzó adatokat. 

Az adatokat Szél Bernadett országgyűlési képviselő szerezte meg közérdekű adatigénylés keretében az Országos Tisztifőorvostól, 
majd az adatok elérhetőségét egy [facebook bejegyzésben](https://www.facebook.com/szelbernadett/photos/a.171247126321571/3708494705930111/?type=3&theater)
megosztotta a nyilvánossággal is. 
Az adatok kezelője a Nemzeti Népegészségügyi Központ. 

**Az adatok formátuma, felépítése**

Az adatok táblázatos formában (Google Sheets) érhetőek el:
[Szoc_otthonok_COVID-19_tábla_megyék_21.03.05_küldésre.xlsx]("https://drive.google.com/drive/folders/1yitS_a8PhZ30KREQN_iuoVjVaA-j7KZG?fbclid=IwAR3JFgtNEmEXbNmg-zk2fZ2v86LnZ1Si0Gxly7qUj08Ym7an33xiGUQDvSY").
A térkép előállításához a dokumentum 2-20. lapját használtam fel.


### Térképi adatok

A térkép adatok forrása az [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Main_Page) (későbbiekben OSM) szabad licencű térinformatikai adatbázis. 
