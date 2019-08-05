#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *
import hashlib

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


@get("/")
def main():
    """Glavna stran."""
    username = get_user()
    cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
" JOIN model ON avto.id_model = model.id_model" +
" JOIN znamka ON znamka.id_znamka = model.id_znamka")
    return template('avtomobili.html', avto=cur, ponudba=None, username=username[0]) 


@post('/')
def avtomobili_filter():
    search = request.forms.search.lower()
    username = get_user()
    if search == '':
        cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
        " JOIN model ON avto.id_model = model.id_model" +
        " JOIN znamka ON znamka.id_znamka = model.id_znamka")
        return template('avtomobili.html', avto=cur, ponudba=None, username=username[0])
    napaka = None
    sez = search.split(':') 
    cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
        " JOIN model ON avto.id_model = model.id_model" +
        " JOIN znamka ON znamka.id_znamka = model.id_znamka WHERE LOWER(znamka) LIKE %s"
                "OR LOWER(model) LIKE %s"
                "OR LOWER(gorivo) LIKE %s"
                "OR CAST(kw AS varchar(10)) LIKE  %s"
                "OR CAST(velikost_motorja AS varchar(10)) LIKE %s"
                "OR CAST(prevozeni_kilometri AS varchar(10)) LIKE %s"
                "OR CAST(zacetna_cena AS varchar(10)) LIKE %s"                ,
                7 *['%' + search + '%'])
    return template('avtomobili.html', avto=cur, ponudba=None, username=username[0])

@get('/avto/:x/')
def avto_get(x):
    username = get_user()
    cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
    " JOIN model ON avto.id_model = model.id_model" +
    " JOIN znamka ON znamka.id_znamka = model.id_znamka WHERE id_avto=%s", [int(x)])
    sez = cur.fetchone()
    cur.execute("SELECT ponudnik, ponujena_cena FROM ponudba AS ponudbe WHERE avto=%s", [x])
    return template('avto.html', x=x, ponudbe=cur, znamka=sez[1], model=sez[2], gorivo=sez[3], prevozeni_kilometri=sez[4], velikost_motorja=sez[5], kw=sez[6], cena=sez[7], ponudba=None, username=username[0])

@post('/avto/:x/')
def avto_post(x):
    username = get_user()
    ponudba = request.forms.ponudba
    cur.execute("SELECT id_avto, znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
    " JOIN model ON avto.id_model = model.id_model" +
    " JOIN znamka ON znamka.id_znamka = model.id_znamka WHERE id_avto=%s", [x])
    sez = cur.fetchone()
    cur.execute("SELECT id_oseba FROM oseba WHERE username=%s", [username])
    ponudnik = cur.fetchone()[0]
    cur.execute("INSERT INTO ponudba (ponudnik, avto, ponujena_cena) VALUES (%s, %s, %s)",
                  [ponudnik, x, int(ponudba)])
    cur.execute("SELECT ponudnik, ponujena_cena FROM ponudba AS ponudbe WHERE avto=%s", [x])
    return template('avto.html', x=x, ponudbe=cur, znamka=sez[1], model=sez[2], gorivo=sez[3], prevozeni_kilometri=sez[4], velikost_motorja=sez[5], kw=sez[6], cena=sez[7], ponudba=None, username=username[0])


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
    return template("sporocilo.html", username=username, sporocila=sporocila, pogovori=pogovori, useers=useers)

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



######################################################################
# Glavni program

# priklopimo se na bazo

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8000/
run(host='localhost', port=8000)
