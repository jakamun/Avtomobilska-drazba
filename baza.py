#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *
#import bottle
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

#@get('/')
#def index():
#    cur.execute("SELECT * FROM oseba ORDER BY priimek, ime")
#    return template('osebe.html', osebe=cur)

@get("/")
def main():
    """Glavna stran."""
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na login, če
    # nima cookija)
    cur.execute("SELECT znamka, model, gorivo, prevozeni_kilometri, velikost_motorja, kw, cena  FROM avtomobil AS avto" +
" JOIN model ON avto.id_model = model.id_model" +
" JOIN znamka ON znamka.id_znamka = model.id_znamka")
    # Vrnemo predlogo za glavno stran
    return template('avtomobili.html', avto=cur)


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
        return template("login.html",
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")


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
        return template("register.html",
                               username=username,
                               napaka='To uporabniško ime je že zavzeto')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return template("register.html",
                               username=username,
                               napaka='Gesli se ne ujemata')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_md5(password1)
        c.execute("INSERT INTO oseba (ime, priimek, racun, rojstvo, kraj, je_cenilec, cena, ocena, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  (ime, priimek, racun, rojstvo, kraj, je_cenilec, cena, ocena, username, password))
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")


######################################################################
# Glavni program

# priklopimo se na bazo

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8000/
run(host='localhost', port=8000)
