import sqlite3
import datetime

DB_NAME = "orientare_cariera.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilizatori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT,
            email TEXT,
            telefon TEXT,
            varsta INTEGER,
            descriere TEXT,
            raport_ai TEXT,
            data_creare TEXT
        )
    """)
    conn.commit()
    conn.close()

def salveaza_utilizator(nume, email, telefon, varsta, descriere, raport_ai):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_curenta = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO utilizatori (nume, email, telefon, varsta, descriere, raport_ai, data_creare)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nume, email, telefon, varsta, descriere, raport_ai, data_curenta))
    conn.commit()
    conn.close()

def extrage_istoric():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nume, email, telefon, varsta, data_creare FROM utilizatori ORDER BY id DESC")
    randuri = cursor.fetchall()
    conn.close()
    return randuri
