# uvozimo ustrezne podatke za povezavo

from bottle import *
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
import hashlib

import auth
auth.db = "sem2019_%s" % auth.user

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def uvozi_podatke():
    with open("oseba.csv") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            r = [None if x in ('', '-') else x for x in r]
            cur.execute("""
                INSERT INTO oseba
                (id_oseba, ime, priimek, rojstvo, racun,
                 je_cenilec, kraj, ocena, cena)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_oseba
            """, r)
            rid, = cur.fetchone()
            print("Uvožena oseba %s z ID-jem %d" % (r[0], rid))
    conn.commit()

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
