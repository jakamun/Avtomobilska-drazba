#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *
import hashlib
import datetime

# uvozimo ustrezne podatke za povezavo
import auth_public as auth



# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# Skrivnost za kodiranje cookijev
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"

# odkomentiraj, če želiš sporočila o napakah
# debug(True)

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


#@get('/')
#def index():
#    cur.execute("SELECT * FROM oseba ORDER BY priimek, ime")
#    return template('osebe.html', osebe=cur)


def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


def get_user(auto_login = True):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        c = conn.cursor()
        c.execute("SELECT username FROM oseba WHERE username=%s",
                  [username])
        r = c.fetchone()
        c.close ()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    if auto_login:
        redirect('/login/')
    else:
        return None

max_cas = datetime.timedelta(hours=5)

def potekel_cas(cas):
    '''izracuna koliko casa je minilo od zadnje podane ponudbe'''
    trenutni_cas = datetime.datetime.now()
    return trenutni_cas - cas

def potekla_drazba(cas):
    '''izračuna če je dražba že potekla in vrne true ali false'''
    if potekel_cas(cas) >= max_cas:
        return True
    else:
        return False


def stanje_drazbe(avto):
    '''za avto vrne ali je dražba potekl ali ne ali pa se sploh še ni začela'''
    cur.execute("SELECT MAX(cas) FROM ponudba WHERE avto=%s", [avto])
    zadnja_ponudba = cur.fetchone()[0]
    if zadnja_ponudba == None:
        return('Še ni ponudbe')
    elif potekla_drazba(zadnja_ponudba):
        return('Dražba je potekla')
    else:
        return('Dražba poteka')

@get("/")
def main():
    """Glavna stran."""
    username = get_user()
    cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
                " JOIN model ON avto.id_model = model.id_model" +
                " JOIN znamka ON znamka.id_znamka = model.id_znamka")
    avto = cur.fetchall()
    sez = []
    for i in avto:
        vrstica = list(i)
        vrstica.append(stanje_drazbe(vrstica[0]))
        sez.append(tuple(vrstica))
    return template('avtomobili.html', avto=sez, username=username[0]) 


@post('/')
def avtomobili_filter():
    search = request.forms.search.lower()
    username = get_user()
    if search == '':
        cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
        " JOIN model ON avto.id_model = model.id_model" +
        " JOIN znamka ON znamka.id_znamka = model.id_znamka")
        avto = cur.fetchall()
        sez = []
        for i in avto:
            vrstica = list(i)
            vrstica.append(stanje_drazbe(vrstica[0]))
            sez.append(tuple(vrstica))
        return template('avtomobili.html', avto=sez, username=username[0])
    else:
        cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
            " JOIN model ON avto.id_model = model.id_model" +
            " JOIN znamka ON znamka.id_znamka = model.id_znamka WHERE LOWER(znamka) LIKE %s"
                    "OR LOWER(model) LIKE %s"
                    "OR LOWER(gorivo) LIKE %s"
                    "OR CAST(kw AS varchar(10)) LIKE  %s"
                    "OR CAST(velikost_motorja AS varchar(10)) LIKE %s"
                    "OR CAST(prevozeni_kilometri AS varchar(10)) LIKE %s"
                    "OR CAST(zacetna_cena AS varchar(10)) LIKE %s",
                    7 *['%' + search + '%'])
        avto = cur.fetchall()
        sez = []
        for i in avto:
            vrstica = list(i)
            vrstica.append(stanje_drazbe(vrstica[0]))
            sez.append(tuple(vrstica))
        return template('avtomobili.html', avto=sez, username=username[0])


@get('/avto/:x/')
def avto_get(x):
    username = get_user()
    cur.execute("SELECT znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
    " JOIN model ON avto.id_model = model.id_model" +
    " JOIN znamka ON znamka.id_znamka = model.id_znamka WHERE id_avto=%s", [int(x)])
    avto = list(cur.fetchone())
    avto.append(stanje_drazbe(x))
    cur.execute("SELECT username, cas, ponujena_cena FROM ponudba" +
                " JOIN oseba ON ponudba.ponudnik=oseba.id_oseba" +
                " WHERE avto = %s", [x])
    ponudbe = cur.fetchall()
    cur.execute("SELECT MAX(cas) FROM ponudba WHERE avto=%s", [x])
    zadnja_ponudba = cur.fetchone()[0]
    cur.execute("SELECT MAX(ponujena_cena) FROM ponudba WHERE avto=%s", [x])
    max_ponudba = cur.fetchone()
    if avto[-1] == 'Dražba je potekla':
        return template('avto.html', x=x, ponudbe=ponudbe, avto=avto, username=username[0], cas=potekel_cas(zadnja_ponudba),
                            max_ponudba=max_ponudba[0], ponudba=None, napaka = 'Dražba je zaključena')
    elif avto[-1] == 'Še ni ponudbe':
        return template('avto.html', x=x, ponudbe=ponudbe, avto=avto, username = username[0], ponudba=None, napaka = None)
    else:
        return template('avto.html', x=x, ponudbe=ponudbe, avto=avto, username = username[0], cas=potekel_cas(zadnja_ponudba),
                        max_ponudba=max_ponudba[0], ponudba=None, napaka = None)


@post('/avto/:x/')
def avto_post(x):
    username = get_user()
    ponudba = request.forms.ponudba
    cur.execute("SELECT znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
        " JOIN model ON avto.id_model = model.id_model" +
        " JOIN znamka ON znamka.id_znamka = model.id_znamka WHERE id_avto=%s", [x])
    avto = list(cur.fetchone())
    avto.append(stanje_drazbe(x))
    cur.execute("SELECT username, cas, ponujena_cena FROM ponudba" +
                " JOIN oseba ON ponudba.ponudnik=oseba.id_oseba" +
                " WHERE avto = %s", [x])
    ponudbe = cur.fetchall()
    cur.execute("SELECT MAX(cas) FROM ponudba WHERE avto=%s", [x])
    zadnja_ponudba = cur.fetchone()[0]
    cur.execute("SELECT MAX(ponujena_cena) FROM ponudba WHERE avto=%s", [x])
    max_ponudba = cur.fetchone()[0]
    if avto[-1] == 'Dražba je potekla':
        return template('avto.html', x=x, ponudbe=ponudbe, avto=avto, username=username[0], cas=potekel_cas(zadnja_ponudba),
                        max_ponudba=max_ponudba, ponudba=None, napaka = 'Dražba je zaključena')
    elif (len(ponudbe) == 0) and (int(avto[-2]) > int(ponudba)):
        return template('avto.html', x=x, ponudbe=ponudbe, avto=avto, ponudba=None, cas=None, 
                        max_ponudba=max_ponudba, username=username[0], napaka = 'Ponudba mora biti višja od izklicne cene')
    elif (len(ponudbe) > 0) and (int(ponudba) <= int(max_ponudba)):
        return template('avto.html', x=x, ponudbe=ponudbe, avto=avto, ponudba=None, cas=potekel_cas(zadnja_ponudba),
                        max_ponudba=max_ponudba, username=username[0], napaka='Ponuditi morate več od trenutne najvišje ponudbe')
    else:
        cur.execute("SELECT id_oseba FROM oseba WHERE username=%s", [username])
        ponudnik = cur.fetchone()[0]
        cur.execute("INSERT INTO ponudba (ponudnik, avto, ponujena_cena) VALUES (%s, %s, %s)",
                    [ponudnik, x, int(ponudba)])
        cur.execute("SELECT cas, max_ponudba FROM ponudba"+
                    " JOIN (SELECT avto, MAX(ponujena_cena) AS max_ponudba"+
                    " FROM ponudba WHERE avto=%s"+
                    "GROUP BY avto) AS nova ON nova.max_ponudba = ponudba.ponujena_cena", [x])
        max_ponudba = cur.fetchone()
        cur.execute("SELECT username, cas, ponujena_cena FROM ponudba" +
                " JOIN oseba ON ponudba.ponudnik=oseba.id_oseba" +
                " WHERE avto = %s", [x])
        ponudbe = cur.fetchall()
        return template('avto.html', x=x, ponudbe=ponudbe, avto=avto, ponudba=None, 
                        cas=potekel_cas(max_ponudba[0]), max_ponudba=max_ponudba[1], username=username[0], napaka=None)


@get("/login/")
def login_get():
    """Serviraj formo za login."""
    return template("login.html",
                           napaka=None,
                           username=None)


@post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    c = conn.cursor()
    c.execute("SELECT 1 FROM oseba WHERE username=%s AND password=%s",
              [username, password])
    if c.fetchone() is None:
        # Username in geslo se ne ujemata
        return template("login.html", napaka='Nepravilna prijava', username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

@get("/novo_geslo/")
def novo_geslo_get():
    """Prikaži formo za geslo."""
    return template("novo_geslo.html", username=None, napaka=None)


@post("/novo_geslo/")
def novo_geslo_post():
    username = request.forms.username
    password = password_md5(request.forms.password)
    c = conn.cursor()
    c.execute("SELECT 1 FROM oseba WHERE username=%s", [username])
    if c.fetchone() is None:
        # Uporabnik ne obstaja
        return template("novo_geslo.html", username=None, napaka='To uporabniško ime ne obstaja.')
    else:   
        c.execute("UPDATE oseba SET password=%s WHERE username=%s",
              [password, username])
    redirect('/')

@get("/logout/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    response.delete_cookie('username')
    redirect('/login/')


@get("/register/")
def register_get():
    """Prikaži formo za registracijo."""
    return template("register.html", ime=None, priimek=None, racun=None, rojstvo=None,
                          kraj=None, je_cenilec=None, cena=None, ocena=None, username=None, napaka=None)


@post("/register/")
def register_post():
    """Registriraj novega uporabnika."""
    ime = request.forms.ime
    priimek = request.forms.priimek
    racun = request.forms.racun
    rojstvo = request.forms.rojstvo
    kraj = request.forms.kraj
    je_cenilec = request.forms.je_cenilec
    ocena = request.forms.ocena
    cena = request.forms.cena
    username = request.forms.username
    password1 = request.forms.password1
    password2 = request.forms.password2
    # Ali uporabnik že obstaja?
    c = conn.cursor()
    c.execute("SELECT 1 FROM oseba WHERE username=%s", [username])
    if c.fetchone():
        # Uporabnik že obstaja
        return template("register.html", ime=ime, priimek=priimek, racun=racun, rojstvo=rojstvo, kraj=kraj, 
            je_cenilec=je_cenilec, cena=cena, ocena=ocena, username=None, napaka='To uporabniško ime je zasedeno.')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return template("register.html", ime=ime, priimek=priimek, racun=racun, rojstvo=rojstvo, kraj=kraj, 
            je_cenilec=je_cenilec, cena=cena, ocena=ocena, username=username, napaka='Gesli se ne ujemata.')
    elif je_cenilec=='TRUE':
        if cena == '':
            return template("register.html", ime=ime, priimek=priimek, racun=racun, rojstvo=rojstvo, kraj=kraj, 
            je_cenilec=je_cenilec, cena=cena, ocena=ocena, username=username, napaka='Navedi koliko računaš')
        elif ocena == '':
            return template("register.html", ime=ime, priimek=priimek, racun=racun, rojstvo=rojstvo, kraj=kraj, 
            je_cenilec=je_cenilec, cena=cena, ocena=ocena, username=username, napaka='Če si cenilec se moraš oceniti')
        elif int(ocena) not in range(0,11):
            return template("register.html", ime=ime, priimek=priimek, racun=racun, rojstvo=rojstvo, kraj=kraj, 
            je_cenilec=je_cenilec, cena=cena, ocena=ocena, username=username, napaka='Ocena mora biti med 1 in 10')
        else:
            # Vse je v redu, vstavi novega uporabnika v bazo
            password = password_md5(password1)
            c.execute("INSERT INTO oseba (ime, priimek, racun, rojstvo, kraj, je_cenilec, cena, ocena, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (ime, priimek, racun, rojstvo, kraj, je_cenilec, cena, ocena, username, password))
            # Daj uporabniku cookie
            response.set_cookie('username', username, path='/', secret=secret)
            redirect("/")
    elif je_cenilec == 'FALSE' and cena == '' and ocena == '':
        password = password_md5(password1)
        c.execute("INSERT INTO oseba (ime, priimek, racun, rojstvo, kraj, je_cenilec, cena, ocena, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  (ime, priimek, racun, rojstvo, kraj, je_cenilec, None, None, username, password))
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_md5(password1)
        c.execute("INSERT INTO oseba (ime, priimek, racun, rojstvo, kraj, je_cenilec, cena, ocena, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  (ime, priimek, racun, rojstvo, kraj, je_cenilec, None, None, username, password))
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")


@get("/sporocilo/")
def get_komentar():
    username = get_user()
    cur.execute("SELECT id_oseba FROM oseba WHERE username=%s", [username])
    id_oseba = cur.fetchone()[0]
    cur.execute(
    """SELECT cas, komentator, prejemnik, sporocilo
       FROM komentar
       WHERE (prejemnik = %s OR komentator = %s)
       ORDER BY cas desc""", [id_oseba, id_oseba])
    sporocila = tuple(cur)
    pogovori = []
    for (cas, prejemnik, posiljatelj, sporocilo) in sporocila:
        if (prejemnik != username) and (prejemnik not in pogovori):
            pogovori.append(prejemnik)
        elif (posiljatelj != username) and (posiljatelj not in pogovori):
            pogovori.append(posiljatelj)
    cur.execute("""SELECT username FROM oseba""")
    users = tuple(cur)
    useers = []
    for user in users:
        useers += user
    return template("sporocilo.html", username=username[0], sporocila=sporocila, pogovori=pogovori, useers=useers)

@post("/sporocilo/")
def post_komentar():
    username = get_user()
    cur.execute("SELECT id_oseba FROM oseba WHERE username=%s", [username])
    id_oseba = cur.fetchone()[0]
    user = request.forms.user
    cur.execute("SELECT id_oseba FROM oseba WHERE username=%s", [user])
    id_user = cur.fetchone()[0]
    spor = request.forms.spor
    cur.execute("INSERT INTO komentar (komentator, prejemnik, sporocilo) VALUES (%s, %s, %s)",
              [id_oseba, id_user, spor])
    return redirect("/sporocilo/")

@get("/user/:x/")
def uporabnik(x):
    username = get_user()
    cur.execute("""SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena, max_moja_ponudba, MAX(ponujena_cena) AS max_ponudba FROM avtomobil AS avto
                JOIN model ON avto.id_model = model.id_model
                JOIN znamka ON znamka.id_znamka = model.id_znamka
                JOIN (SELECT avto, ponudnik, max(ponujena_cena) AS max_moja_ponudba FROM ponudba
                JOIN oseba ON oseba.id_oseba=ponudba.ponudnik
                WHERE username=%s
                GROUP BY avto, ponudnik) AS pon ON avto.id_avto = pon.avto
                JOIN ponudba ON ponudba.avto = avto.id_avto
                GROUP BY id_avto, znamka, model, max_moja_ponudba""", [username])
    avto = cur.fetchall()
    koncane = []
    aktivne = []
    for i in avto:
        vrstica = list(i)
        stanje = stanje_drazbe(vrstica[0])
        if stanje == 'Dražba poteka':
            aktivne.append(tuple(vrstica))
        else:
            if vrstica[-1] == vrstica[-2]:
                vrstica.append('ZMAGOVALEC')
                koncane.append(tuple(vrstica))
            else:
                vrstica.append('PORAŽENEC')
                koncane.append(tuple(vrstica))
    return template('user.html', koncane=koncane, aktivne=aktivne, username=username[0])

@get("/cenilci/")
def get_cenilci():
    username = get_user()
    cur.execute("""SELECT id_oseba, ime, priimek, racun, kraj, ocena, cena FROM oseba where je_cenilec=TRUE""")
    return template('cenilci.html', oseba=cur, username=username)

@get("/cenilec/:x/")
def get_cenilec(x):
    username = get_user()
    cur.execute("SELECT ime, priimek, racun, kraj, ocena, cena, username FROM oseba WHERE id_oseba=%s", [x])
    sez = cur.fetchone()
    return template('cenilec.html',ime=sez[0], priimek=sez[1], racun=sez[2], kraj=sez[3], ocena=sez[4], cena=sez[5], uporabnik=sez[6], username=username)

@post("/cenilec/:x/")
def post_cenilec(x):
    username = get_user()
    ocena = request.forms.ocena
    cur.execute("INSERT INTO ocena_cenilca (id_cenilec, dana_ocena) VALUES (%s, %s)", [x, ocena])
    return redirect("/cenilci/")

######################################################################
# Glavni program

# priklopimo se na bazo

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8000/
run(host='localhost', port=8000)
