import pandas 
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

df = pandas.read_excel(os.path.join(BASE_DIR, 'magazyn.ods'), engine='odf', dtype={"ind_kod_kreskowy": str}) # We need to specify ean beacuse if there are 0s at the beginning of the ean, they will be removed

df["ind_kod_kreskowy"] = df["ind_kod_kreskowy"].str.replace(".0", "", regex=False) # Remove the ".0" from the ean values

df = df.rename(columns={"ind_nazwa": "name", "ind_kod_kreskowy": "ean", "wms_pozycja": "location"})

df["ean"] = df["ean"].fillna("") # Fill NaN (Not a number) values in the ean column with an empty string

df["location"] = df["location"].fillna("") # Same thing
 
conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db")) # Create a connection to the SQLite database

df.to_sql('products', conn, if_exists='replace', index=False) # Convert the DataFrame to a SQL table

conn.close() 

print(f"Data imported successfully into the database. Total records: {len(df)}")

