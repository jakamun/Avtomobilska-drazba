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


def poisci_podatke(block):  
    sample = re.compile(
        r'(?P<znamka>\w+\s+\w+).*'
        r'<li>(?P<prevozeni_kilometri>\d+)\skm.*'
        r'<li>(?P<gorivo>\w+)\s'
        r'motor,\s(?P<velikost_motorja>\d+)\sccm,\s'
        r'(?P<kW>\d+).*'
        r'(REDNA\sOBJAVA\sCENE|AKCIJSKA\sCENA).*?(?P<cena>\d{1,3}\.\d+).*\x80.*',
        re.DOTALL
    )
    for expression in sample.finditer(block):
        dict = expression.groupdict()
    return dict

def pridobi_slovar(directory, filename):
    webpage = read_file_to_string(directory, filename)
    list_of_ads = razdeli_na_dele(webpage)
    list_of_dicts = []
    for i in range(0, len(list_of_ads)):
        list_of_dicts.append(poisci_podatke(list_of_ads[i]))
    return list_of_dicts


def zapisi_csv(fieldnames, rows, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return None


def zapisi_podatke_v_csv(list_of_dicts_ads, directory, filename):
    fieldnames = ['znamka', 'prevozeni_kilometri', 'gorivo', 'velikost_motorja','kW', 'cena']
    zapisi_csv(fieldnames, list_of_dicts_ads, directory, filename)
    return None

directory_name = 'uvoz_podatkov'

url_audi = ('https://www.avto.net/Ads/results.asp?znamka=Audi&model=&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=1000&cenaMax=999999&letnikMin=0&letnikMax=2090&bencin=0&starost2=1&oblika=11,%2012,%2013,%2014,%2016,%2017,%2015,%2018&ccmMin=0&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=9999999&kwMin=&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1000000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1000100020&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&zaloga=1&arhiv=&presort=&tipsort=&stran=')
html_audi = 'audi.html'
csv_audi = 'audi.csv'


#koda
read_file_to_string

prenesi_url(url_audi)

shrani_stran(url_audi, directory_name, html_audi)

audi = read_file_to_string(directory_name, html_audi)

audi_reg = razdeli_na_dele(audi)

zapisi_podatke_v_csv(pridobi_slovar(directory_name, html_audi), directory_name, csv_audi)



for i in range(0,48):
    print(poisci_podatke(audi_reg[i]))

# OPOMBA: za oglase izberi oglase, ki imajo avte na zalogi in tiste, ki so nad 1000 €, samo rabljeno