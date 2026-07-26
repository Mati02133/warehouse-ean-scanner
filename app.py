from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__) # Create a Flask application instance

app.secret_key = os.environ.get("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=30) # Set the session lifetime

ACCESS_CODE = os.environ.get("ACCESS_CODE")


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row # This allows us to access the columns by name instead of index(product["name"] instead of product[0])
    return conn
@app.before_request

def require_access():
    allowed_routes = ["access", "static"]
    if request.endpoint not in allowed_routes and not session.get("has_access"):
        return redirect(url_for("access"))

@app.route("/access", methods=["GET", "POST"])
def access():
    error = None
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if code == ACCESS_CODE:
            session.permanent = True
            session["has_access"] = True 
            return redirect(url_for("index"))
        else:
            error = "Invalid access code."

    code_from_url = request.args.get("code", "").strip()
    if code_from_url and code_from_url == ACCESS_CODE:
        session.permanent = True
        session["has_access"] = True
        return redirect(url_for("index"))
    return render_template("access.html", error=error)


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