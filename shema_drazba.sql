CREATE TABLE IF NOT EXISTS oseba (
    id INTEGER PRIMARY KEY
    ime TEXT NOT NULL
    priimek TEXT NOT NULL
    rojstvo DATE NOT NULL
    kraj TEXT NOT NULL
    trr INTEGER UNIQUE NOT NULL
    je_cenilec BOOLEAN NOT NULL
    ocena INTEGER
    cena INTEGER 
)
CREATE TABLE IF NOT EXISTS uporabnik (
    id INTEGER REFERENCES oseba(id)
    geslo TEXT NOT NULL
)

CREATE TABLE avtomobil (
    serijska_stevilka INTEGER PRIMARY KEY
    gorivo TEXT NOT NULL
    zacetna_cena INTEGER 
    dejanska_vrednost INTEGER NOT NULL
    velikost_motorja INTEGER NOT NULL
    kW INTEGER NOT NULL   
)

CREATE TABLE znamka (
    serijska_stevilka INTEGER REFERENCES avtomobil(serijska_stevilka)
    znamka TEXT NOT NULL
)

CREATE TABLE model (
    serijska_stevilka INTEGER REFERENCES avtomobil(serijska_stevilka)
    model TEXT NOT NULL
)

CREATE TABLE ponudba (
    
)