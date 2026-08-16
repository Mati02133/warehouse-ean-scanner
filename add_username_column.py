import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE audit_logs ADD COLUMN username TEXT")
    conn.commit()
    print("Kolumna 'username' dodana do audit_logs.")
except sqlite3.OperationalError as e:
    print(f"Nie udało się dodać kolumny: {e}")

conn.close()