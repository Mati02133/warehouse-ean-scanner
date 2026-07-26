from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__) # Create a Flask application instance

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row # This allows us to access the columns by name instead of index(product["name"] instead of product[0])
    return conn


@app.route("/", methods=["GET", "POST"])

def index():
    result = None
    error = None
    if request.method == "POST":
        ean = request.form.get("ean", "").strip() # Get the ean
        conn = get_db_connection()
        product = conn.execute("SELECT name, location FROM products WHERE ean = ?", (ean,)).fetchone()
        conn.close()
        if product:
            result = {"name": product["name"], "location": product["location"]}
        else:
            error = f"Product with EAN {ean} not found in the database."
    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True) # Run the Flask application in debug mode