import sqlite3
import datetime

DB_NAME = "orientare_cariera.db"

def init_db():
    """Creează tabelul și asigură adăugarea coloanelor noi pe server."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Creăm structura de bază dacă nu există
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
    
    # 2. Forțăm adăugarea coloanei 'email' dacă serverul a rămas pe baza veche
    try:
        cursor.execute("ALTER TABLE utilizatori ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # Dacă există deja coloana, ignorăm eroarea
        
    # 3. Forțăm adăugarea coloanei 'telefon' dacă serverul a rămas pe baza veche
    try:
        cursor.execute("ALTER TABLE utilizatori ADD COLUMN telefon TEXT")
    except sqlite3.OperationalError:
        pass  # Dacă există deja coloana, ignorăm eroarea

    conn.commit()
    conn.close()

def salveaza_utilizator(nume, email, telefon, varsta, descriere, raport_ai):
    """Salvează toate datele clientului în baza de date locală."""
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
    """Extrage contactele clienților pentru panoul administrativ."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nume, email, telefon, varsta, data_creare FROM utilizatori ORDER BY id DESC")
    randuri = cursor.fetchall()
    conn.close()
    return randuri
