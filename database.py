import sqlite3
import datetime

DB_NAME = "orientare_cariera.db"

def init_db():
    """Creează tabelul în baza de date dacă nu există deja."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilizatori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT,
            varsta INTEGER,
            descriere TEXT,
            raport_ai TEXT,
            data_creare TEXT
        )
    """)
    conn.commit()
    conn.close()

def salveaza_utilizator(nume, varsta, descriere, raport_ai):
    """Inserează un nou utilizator și raportul lui în baza de date."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_curenta = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO utilizatori (nume, varsta, descriere, raport_ai, data_creare)
        VALUES (?, ?, ?, ?, ?)
    """, (nume, varsta, descriere, raport_ai, data_curenta))
    conn.commit()
    conn.close()

def extrage_istoric():
    """Returnează toți utilizatorii salvați ordonați descrescător după ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nume, varsta, data_creare FROM utilizatori ORDER BY id DESC")
    randuri = cursor.fetchall()
    conn.close()
    return randuri
