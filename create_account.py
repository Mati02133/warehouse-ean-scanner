import sqlite3
import os
from datetime import datetime, timezone
from getpass import getpass
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

username = input("PODAJ NOWY LOGIN: ").strip()
password = getpass("HASLO: ")
password_confirm = getpass("POWTORZ HASLO ")
if not password or not username:
    print("LOGIN I HASLO NIE MOGA BYC PUSTE")
    exit()
if password != password_confirm:
    print("HASLA SIE NIE ZGADZAJA")
    exit()

password_hash = generate_password_hash(password)
created_at = datetime.now(timezone.utc).isoformat()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)", (username, password_hash, created_at))
    conn.commit()
    print(f"DODANO KONTO: {username}")
except sqlite3.IntegrityError:
    print("TEN LOGIN JUZ ISTNIEJE")

conn.close()