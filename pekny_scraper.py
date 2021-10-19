from sqlite3.dbapi2 import InternalError
import requests
import pandas
import csv
import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import os
from datetime import date, datetime

datum_prep = datetime.now()
#datum_prep = datetime.today()
#datum = datum_prep.strftime("%d/%m/%Y")
datum = datum_prep.strftime("%H:%M:%S")
print(datum)

jmena_parametru_global = ["Číslo inzerátu",
                          "Dispozice",
                          "Stav",
                          "Plocha",
                          "Cena",
                          "Město",
                          "Městská část",
                          "Typ vlastnictví",
                          "Typ budovy",
                          "PENB",
                          "Vybavenost",
                          "Podlaží",
                          "Balkón",
                          "Terasa",
                          "Sklep",
                          "Lodžie",
                          "Parkování",
                          "Výtah",
                          "Garáž",
                          "K dispozici od",
                          "Rekonstrukce"]  # jména všech možných parametrů co bývají v inzerátu

pocetstranek = 0  # pocet stranek na webu
stranky_list = []
seznam_parametru = []
stranky_pomoc = []
insert_parametry = []
pepa = []


def get_links():
    # zde získávám obsah 1.stránky
    get_bezrealitky = requests.get(
        ("https://www.bezrealitky.cz/vypis/nabidka-prodej/byt?page=1"))
    source_bezrealitky = get_bezrealitky.content
    soup_bezrealitky = BeautifulSoup(
        source_bezrealitky, features="html.parser")
    for link in soup_bezrealitky.find_all('a'):  # získávám odkazy
        stranky_pomoc.append(link.get("href"))
    return stranky_pomoc


def pocet_stranek():
    for stranka in stranky_pomoc:
        if "page" in stranka:
            stranky_list.append(stranka)
            #print("stranka appended")
    if len(stranky_list) < 1:
        raise Exception("len stranky_list < 1")
    # vezmu předposlední link na stránku (poslední je "next"), vezmu to za =, range funkce jde do x-1
    pocetstranek = int(stranky_list[-2].split("=")[1])+1


def ziskani_inzeratu_a_obsahu():
    index = 1
    global inzeraty
    for x in range(1, 3):  # misto cisla pak pocetstranek
        web = ("https://www.bezrealitky.cz/vypis/nabidka-prodej/byt?page=" + str(x))
        get_bezrealitky = requests.get(web)  # zde získávám obsah 1.stránky
        source_bezrealitky = get_bezrealitky.content
        soup_bezrealitky = BeautifulSoup(
            source_bezrealitky, features="html.parser")

        stranky_pomoc = []
        for link in soup_bezrealitky.find_all('a'):  # získávám odkazy
            stranky_pomoc.append(link.get("href"))

        for stranka in stranky_pomoc:
            if "page" in stranka:
                stranky_list.append(stranka)

        hrefy = []
        for link in soup_bezrealitky.find_all('a'):
            hrefy.append(link.get("href"))

        odkazy = []
        for href in hrefy:
            if "nemovitosti-byty-domy" in href:
                odkazy.append(href)

        # za každou fotku se tam objeví jeden link, setem udělám unique, dávám na list aby se s tím dalo pracovat
        odkazy = list(set(odkazy))

        link = "https://www.bezrealitky.cz"  # base link pro odkazovani na inzeraty
        # tvoření linků na jednotlivé inzeráty

        inzeraty = [(link + odkaz) for odkaz in odkazy]

        # PRO INZERÁTY

        for inzerat in inzeraty:
            # zde získám obsah 1. inzerátů na aktuální stránce
            get_inzerat = requests.get(inzerat)
            source_inzerat = get_inzerat.content
            global soup_inzerat
            soup_inzerat = BeautifulSoup(
                source_inzerat, features="html.parser")

            # zde vytahuju tabulku parametrů atd. z aktuálního inzerátu
            inzerat_divy = soup_inzerat.find_all(
                'div', attrs={"class": "col col-6 param-value"})
            vnitrek_divu = [(i.contents[0]) for i in inzerat_divy]

            parametry = []
            for m in vnitrek_divu:  # zde čistím parametry o /n
                m = m.strip()
                parametry.append(m)

            # tím se zbavím prázdného co zbylo po reklamě na internet nebo co
            # parametry.pop(0)
            # parametry.pop(-1)

            seznam_parametru.append(parametry)

            print("Jdu na " + inzerat)

            # zde vytahuju tabulku parametrů atd. z aktuálního inzerátu
            param_divy = soup_inzerat.find_all(
                'div', attrs={"class": "col col-6 param-title"})
            jmena_param = [(i.contents[0]) for i in param_divy]
            jmena_parametry_inzeratu = []
            for m in jmena_param:  # zde čistím parametry o /n
                m = m.strip()
                jmena_parametry_inzeratu.append(m)
            #jmena_parametry_inzeratu = jmena_parametry_inzeratu[1:]

            # print(insert_parametry)
            global pepa
            pepa = []
            for u in jmena_parametru_global:
                if u in jmena_parametry_inzeratu:
                    #print(u +  " je v jmena_parametry_inzeratu")
                    pepa.append(parametry[jmena_parametry_inzeratu.index(u)])
                    # print(pepa)
                else:
                    #print(u + " neni v jmena_parametry_inzeratu")
                    pepa.append("-")
                    # print(pepa)
                    #print("jdu na dalsi u")
                    #print("jdu na dalsi inzerat_________")
            pepa.append("/home/kub/projects/bezrealitky/fotky/" + str(index))
            pepa.append(datum)
            pepa.append(" ")
            index += 1
            insert_parametry.append(pepa)
            # print(insert_parametry)


def zapis_do_csv():
    nazvy_parametru_csv = ["Cislo_inzeratu", "Dispozice", "Stav", "Plocha", "Cena", "Mesto", "Mestska_cast", "Typ_vlast",
                           "Typ_budovy", "PENB", "Vybavenost", "Podlazi", "Balkon", "Terasa", "Sklep", "Lodzie", "Parkovani", "Vytah",
                           "Garaz", "K_dispozici_od", "Rekonstrukce", "Odkaz_fotky", "Vlozeno_datum", "Zmizelo_datum", "Rozdil_dat"]
    # tohle pak oživím až bude třeba dát output do csv
    with open("/home/kub/projects/bezrealitky/csv_parametru.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(nazvy_parametru_csv)
        writer.writerows(insert_parametry)


"""    
import pandas as pd
file_name = "my_file_with_dupes.csv"
file_name_output = "my_file_without_dupes.csv"

df = pd.read_csv(file_name, sep="\t or ,")            tohle využiju na zbavení se duplikátů v csv
df.drop_duplicates(subset=None, inplace=True)

# Write the results to a different file
df.to_csv(file_name_output, index=False)    
"""


def stahovani_obrazku():
    # zde vytahuju fotky z aktuálního inzerátu
    #g = 1
    global konecny_list_img
    konecny_list_img = []
    for inzerat in inzeraty:
        get_inzerat = requests.get(inzerat)
        source_inzerat = get_inzerat.content
        soup_inzerat = BeautifulSoup(
            source_inzerat, features="html.parser")
        inzerat_divy = soup_inzerat.find_all(
            'div', attrs={"class": "detail-slick-item"})
        vnitrek_divu_obrazky = [(i.contents[0]) for i in inzerat_divy]
        inzerat_divy2 = soup_inzerat.find_all("img")

        global list_img
        list_img = []
        for img in inzerat_divy2:
            list_img.append(img["src"])

        # mažu duplikáty, dělám list abych s tím mohl dále pracovat
        list_img = list(set(list_img))
        global cisty_list_img
        cisty_list_img = []
        for item in list_img:  # tento celý blok slouží k vyfiltrování jenom velkých fotek, bez thumbnailů a useless odkazů
            if "jpg" in item:
                if "https" in item:
                    if "thumb" not in item:  # z nějakého fascinujícího důvodu mi nefunguje kombinování více podmínek, dává mi to tam ty krátké odkazy
                        cisty_list_img.append(item)
        # print(cisty_list_img)
        konecny_list_img.append(cisty_list_img)
        # print(konecny_list_img)


def filtr_fotek():
    global cisty_list_img
    cisty_list_img = []
    for item in konecny_list_img:  # tento celý blok slouží k vyfiltrování jenom velkých fotek, bez thumbnailů a useless odkazů
        if "jpg" in item:
            if "https" in item:
                if "thumb" not in item:  # z nějakého fascinujícího důvodu mi nefunguje kombinování více podmínek, dává mi to tam ty krátké odkazy
                    cisty_list_img.append(item)


def ukladani_fotek():
    # pomocný list na tvoření jmen souborů co stáhnu
    a = 1
    # for b in cisty_list_img:
    len_kon_list_img = 0
    for element in konecny_list_img:
        len_kon_list_img += len(element)

    parent_dir = "/home/kub/projects/bezrealitky/fotky"

    for inzerat in konecny_list_img:  # tady stahuju jednotlivé obrázky
        directory = str(a)
        path = os.path.join(parent_dir, directory)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        pocet_fotek_inzeratu = list(range(len(inzerat)))

        for obrazek in inzerat:
            cislo = inzerat.index(obrazek)
            # neumí to vytvořit obrázek když tam je celý odkaz z obrázku, tak musím nejdřív udělat list jmen a ty pak použít
            #print("cislo je " + str(cislo))
            adresa = "/home/kub/fefe/" + \
                str(a) + "/" + str(pocet_fotek_inzeratu[cislo]) + ".jpeg"
            urllib.request.urlretrieve(obrazek, adresa)
        a += 1


def ukladani_fotek_stare():
    # pomocný list na tvoření jmen souborů co stáhnu
    a = 1
    # for b in cisty_list_img:
    ffr = list(range(len(cisty_list_img)))
    parent_dir = "/home/kub/fefe/"
    directory = str(a)
    path = os.path.join(parent_dir, directory)
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    for obrazek in cisty_list_img:  # tady stahuju jednotlivé obrázky

        cislo = cisty_list_img.index(obrazek)
        # neumí to vytvořit obrázek když tam je celý odkaz z obrázku, tak musím nejdřív udělat list jmen a ty pak použít
        #print("cislo je " + str(cislo))
        adresa = "/home/kub/fefe/" + str(a) + "/" + str(ffr[cislo]) + ".jpeg"
        urllib.request.urlretrieve(obrazek, adresa)
    a += 1


def save_to_sql():
    conn = sqlite3.connect('SQLite_Bezrealitky.db')
    cursor = conn.cursor()
    insert_parametry.pop(-1)

    print("Database created and Successfully Connected to SQLite")

    conn.execute('''CREATE TABLE IF NOT EXISTS tab_parametry(       Cislo_inzeratu BLOB    NOT NULL,
                                                                    Dispozice      BLOB    NOT NULL,
                                                                    Stav           BLOB    NOT NULL,
                                                                    Plocha         BLOB    NOT NULL,
                                                                    Cena           BLOB    NOT NULL,
                                                                    Mesto          BLOB,
                                                                    Mestska cast   BLOB,
                                                                    Vlastnictvi    BLOB,
                                                                    Typ budovy     BLOB,
                                                                    PENB           BLOB,
                                                                    Vybavenost     BLOB,
                                                                    Podlazi        BLOB,
                                                                    Balkon         BLOB,
                                                                    Terasa         BLOB,
                                                                    Sklep          BLOB,
                                                                    Lodzie         BLOB,
                                                                    Parkovani      BLOB,
                                                                    Vytah          BLOB,
                                                                    Garaz          BLOB,
                                                                    K dispozici od BLOB,
                                                                    Rekonstrukce   BLOB,
                                                                    Odkaz fotky    BLOB,
                                                                    Datum_pridani  BLOB,
                                                                    Datum_odebrani BLOB
                                                                    )''')
    id_v_db = list(cursor.execute("SELECT Cislo_inzeratu from tab_parametry"))
    global id_v_db_ciste
    id_v_db_ciste = []
    for id in id_v_db:
        id_v_db_ciste.append(id[0])

    for a in insert_parametry:
        print("a[0] je ")
        print(a[0])

        
        # dava none (false) když to nic nenajde, ergo "pokud true"
        """
        if not (cursor.execute("SELECT EXISTS(SELECT Cislo_inzeratu FROM tab_parametry WHERE Cislo_inzeratu = (?))", (a[0],))):
            print(a[0])
            print("Inzerat už v databázi je")
            """
    
        if a[0] in id_v_db_ciste:
          print("Inzerat už v databázi je")  
        else:
            cursor.executemany(
                "INSERT INTO  tab_parametry VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?)", [a])
            print("Inzerát přidán")
# JE TŘEBA PŘIDAT FUNKCI KTERÁ PROJEDE ID V DATABÁZI A POKUD TO (PRO (KAŽDÝ PRVEK ID) IN (PRVNÍ PRVEK LISTŮ))
#  NENAJDE V PRVNÍM PRVKU LISTU LISTŮ PARAMETRŮ, POTOM TO HODÍ AKTUÁLNÍ ČAS
# ? UDĚLAT NOVOU FUNKCI KTERÁ NEJDŘÍV ZCHECKNE TEN ČAS A PŘIDÁ ČAS KDY INZERÁT ZMIZEL

    print("vlozeno")
    cursor.execute("SELECT * FROM tab_parametry")
    rows = cursor.fetchall()
    for row in rows:
        pass
        # print(row)
    conn.commit()
    conn.close()


def datum_odebrani():
    conn = sqlite3.connect('SQLite_Bezrealitky.db')
    cursor = conn.cursor()
    id_v_db = list(cursor.execute("SELECT Cislo_inzeratu from tab_parametry"))
    print("id_v_db:")
    print(id_v_db)
    id_v_db_ciste = []
    for id in id_v_db:
        id_v_db_ciste.append(id[0])
    print(id_v_db_ciste)
    #cislo = ("685199",)
    #cislo2 = str(cislo)
    #print("cislo strip " + cislo2.strip())
    #print("cislo[0] " + cislo[0])
    #if (cislo[0] in id_v_db[0]):
    #    print("JEEEEEEEEEEE")
    #else:
    #    print("NENIIIIIIIIII")
    a = 0
    #
    #cursor.execute("ALTER TABLE tab_parametry ADD Datum_odebrani BLOB")
    print("id v db ciste je:")
    print(id_v_db_ciste)
    for inzerat in insert_parametry:
        #for id in id_v_db_ciste:
        if inzerat[0] in id_v_db_ciste:
            #print("je " + id_v_db_ciste[a])
            cursor.execute("""UPDATE tab_parametry SET Datum_odebrani = ? WHERE Cislo_inzeratu = ?""", ("-", id_v_db_ciste[a]))
        else:   
            print(str(id_v_db_ciste[a]) + "neni")
            cursor.execute("""UPDATE tab_parametry SET Datum_odebrani = (?) WHERE Cislo_inzeratu = (?)""", (datum, id_v_db_ciste[a]))
        print(a)
        a+=1
    conn.commit()
    conn.close()


get_links()
pocet_stranek()
ziskani_inzeratu_a_obsahu()
print("Zapisuju do csv")
zapis_do_csv()
print("Zapisuju do databaze")
save_to_sql()
print("Stahuju obrazky")
# stahovani_obrazku()
# filtr_fotek()
#print("Ukladam obrazky")
# ukladani_fotek()

datum_odebrani()
