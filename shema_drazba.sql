CREATE TABLE IF NOT EXISTS oseba (
    id_oseba INTEGER PRIMARY KEY
    ime TEXT NOT NULL
    priimek TEXT NOT NULL
    rojstvo DATE NOT NULL
    racun INTEGER UNIQUE NOT NULL
    je_cenilec BOOLEAN NOT NULL
    kraj TEXT NOT NULL
    ocena INTEGER
    cena INTEGER 
    
)

CREATE TABLE avtomobil (
    id_avto INTEGER PRIMARY KEY
    id_model INTEGER REFERENCES model(model_id)
    prevozeni_kilometri INTEGER NOT NULL
    gorivo TEXT NOT NULL
    velikost_motorja INTEGER NOT NULL
    kW INTEGER NOT NULL 
    cena INTEGER NOT NULL
    zacetna_cena INTEGER NOT NULL    
)

CREATE TABLE znamka (
    id_znamka INTEGER PRIMARY KEY 
    znamka TEXT NOT NULL
)

CREATE TABLE model (
    id_model INTEGER REFERENCES avtomobil(serijska_stevilka)
    model TEXT NOT NULL
    id_znamka INTEGER REFERENCES znamka(id_znamka)
)

CREATE TABLE ocena (
    id_ocena INTEGER PRIMARY KEY AUTOINCREMENT
    avto INTEGER REFERENCES avtomobil(id_avto)
    kupec INTEGER REFERENCES oseba(id_oseba)
    cenilec INTEGER REFERENCES oseba(id_oseba)
    vrednost INTEGER NOT NULL    
)

CREATE TABLE ponudba (
    id_ponudba INTEGER PRIMARY KEY AUTOINCREMENT
    ponudnik INTEGER REFERENCES oseba(id_oseba)
    avto INTEGER REFERENCES avtomobil(id_avto)
    cena INTEGER NOT NULL

)