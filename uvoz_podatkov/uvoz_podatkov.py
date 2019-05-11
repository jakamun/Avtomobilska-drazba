import requests
import re
import os
import csv


def prenesi_url(url):
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('Napaka!')
        return None
    return r.text


def save_string_to_file(text, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None


def shrani_stran(url, directory, filename):
    text = prenesi_url(url)
    return save_string_to_file(text, directory, filename)


def read_file_to_string(directory, filename):
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf-8') as file_in:
        return file_in.read()


def razdeli_na_dele(webpage):
    sample1 = re.compile(
        r'\<a class=.*\s+<span>'
    )
    sample2 = re.compile(
        r'<!-- OZNAKA GARANCIJE -->'
    )
    list = re.split(sample1, webpage)
    last = list[-1]
    last = re.split(sample2, last)
    list[-1] = last[0]
    return list[1:]


def poisci_podatke(block, reg):
    sample = re.compile(
        reg +
        r'<li>(?P<prevozeni_kilometri>\d+)\skm.*'
        r'<li>(?P<gorivo>\w+)\s'
        r'motor,\s(?P<velikost_motorja>\d+)\sccm,\s'
        r'(?P<kW>\d+).*'
        r'(REDNA\sOBJAVA\sCENE|AKCIJSKA\sCENA).*?(?P<cena>\d{1,3}\.\d+).*\x80.*',
        re.DOTALL
    )
    ujemanje = sample.search(block)
    slovar = ujemanje.groupdict()
    return slovar


def pridobi_slovar(directory, filename, reg):
    webpage = read_file_to_string(directory, filename)
    list_of_ads = razdeli_na_dele(webpage)
    list_of_dicts = []
    for i in range(0, len(list_of_ads)):
        try:
            list_of_dicts.append(poisci_podatke(list_of_ads[i], reg))
        except:
            continue
    return list_of_dicts


def zapisi_csv(fieldnames, rows, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return None


def zapisi_podatke_v_csv(list_of_dicts_ads, directory, filename):
    fieldnames = ['znamka', 'model', 'prevozeni_kilometri', 'gorivo', 'velikost_motorja', 'kW', 'cena']
    zapisi_csv(fieldnames, list_of_dicts_ads, directory, filename)
    return None

# POBRANE SPLETNE STRANI

# znamke = ['Audi', 'BMW', 'Citroen', 'Peugeot', 'Renault', 'Opel', 'Mercedes-Benz', 'Ford', 'Volkswagen', 'Volvo', 'Toyota', 'Fiat', 'Suzuki', 'Nissan', 'Honda', 'Kia']

# for znamka in znamke:
#    url = ('https://www.avto.net/Ads/results.asp?znamka={}&model=&modelID=&tip=&znamka2=&model2=&tip'
#    '2=&znamka3=&model3=&tip3=&cenaMin=0&cenaMax=999999&letnikMin=0&letnikMax=2090&bencin=0&starost2='
#    '1&oblika=11,%2012,%2013,%2014,%2016,%2017,%2015,%2018&ccmMin=0&ccmMax=99999&mocMin=&mocMax=&kmMin='
#    '0&kmMax=9999999&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolz'
#    'inaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&bar'
#    'va=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1000000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&E'
#    'Q7=1000100020&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&bro'
#    'ker=&prikazkategorije=&kategorija=&zaloga=1&arhiv=&presort=&tipsort=&stran=').format(znamka)
#    shrani_stran(url, 'uvoz_podatkov\\spletne_strani', '{}.html'.format(znamka))


directory = 'uvoz_podatkov\\tabele'

# AUDI

regularni_audi = r'(?P<znamka>\w+)\s+(?P<model>\w+).*</span>.*'
zapisi_podatke_v_csv(pridobi_slovar('uvoz_podatkov\\spletne_strani', 'Audi.html', regularni_audi), directory, 'Audi.csv')

# BMW

bmw_regularni = r'(?P<znamka>\w{3})\s.*?:\s(?P<model>(\w|\d)+)\s.*?</span>.*?'
zapisi_podatke_v_csv(pridobi_slovar('uvoz_podatkov\\spletne_strani', 'BMW.html', bmw_regularni), directory, 'BMW.csv')

# Citroen

citr_reg = r'(?P<znamka>Citroen)\s(?P<model>(\w|\d)+)\s.*?</span>.*?'
zapisi_podatke_v_csv(pridobi_slovar('uvoz_podatkov\\spletne_strani', 'Citroen.html', citr_reg), directory, 'Citroen.csv')


# SPLETNE STRANI SO ŽE POBRANE ZA ZAPIS CSV RABIŠ SAMO POGLEDAT KAKO JE ZAPISAN MODEL AVTA IN PRILAGODIŠ REGULARNI IZRAZ
