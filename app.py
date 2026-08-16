from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3
import os
from datetime import timedelta,datetime,timezone
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
import secrets

load_dotenv()

app = Flask(__name__) # Create a Flask application instance

app.secret_key = os.environ.get("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=30) # Set the session lifetime
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"

ACCESS_CODE = os.environ.get("ACCESS_CODE")
ADMIN_SESSION_DAYS = 100
app.permanent_session_lifetime = timedelta(days=ADMIN_SESSION_DAYS)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


limiter = Limiter(get_remote_address, app=app, default_limits=[])

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10) # Set a timeout of 10 seconds for database operations
    conn.row_factory = sqlite3.Row # This allows us to access the columns by name instead of index(product["name"] instead of product[0])
    return conn

def get_current_admin():
    token = session.get("admin_token")
    if not token:
        return None
    conn = get_db_connection()
    row = conn.execute("""
        SELECT sessions.id as session_id, sessions.is_active, users.id as user_id, users.username
        FROM sessions JOIN users ON sessions.user_id = users.id
        WHERE sessions.session_token = ?""",
        (token,)).fetchone()
    conn.close()
    if row is None or row["is_active"] == 0:
        return None
    return {'session_id': row['session_id'],'user_id': row['user_id'], "username":row['username']}


@app.before_request

def require_access():
    allowed_routes = ["access", "static"]
    if request.endpoint not in allowed_routes and not session.get("has_access"):
        return redirect(url_for("access"))

@app.route("/access", methods=["GET", "POST"])
@limiter.limit("5 per 15 minutes") # Limit the number of access attempts to 5 per 15 minutes
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
@app.route("/login", methods = ["GET", "POST"])
@limiter.limit("5 per 15 minutes")
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db_connection()
        user = conn.execute("SELECT id, username, password_hash FROM users WHERE username = ?",(username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            token = secrets.token_hex(32)
            now = datetime.now(timezone.utc).isoformat()
            conn.execute("INSERT INTO sessions (session_token, user_id, created_at, last_active, is_active) VALUES (?, ?, ?, ?, 1)",
            (token, user["id"], now, now)
            )
            conn.commit()
            conn.close()

            session.clear()
            session.permanent = True
            session["admin_token"] = token
            session["has_access"] = True
            return redirect(url_for("index"))
        else:
            conn.close()
            error = "Nieprawidlowy login lub haslo"
    return render_template("login.html", error = error)


@app.route("/logout")
def logout():
    admin = get_current_admin()
    if admin:
        conn = get_db_connection()
        conn.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (admin["session_id"],))
        conn.commit()
        conn.close()
    session.clear()
    return redirect(url_for('access'))

@app.route("/api/search") # Define a route for the API search endpoint
def api_search():
    query = request.args.get("q", "").strip()

    if len(query) < 3:
        return jsonify([])

    conn = get_db_connection()
    results = conn.execute(
        "SELECT name, ean, location FROM products WHERE LOWER(name) LIKE LOWER(?) LIMIT 8",(f"%{query}%",)).fetchall()
    conn.close()
    products = []
    for row in results:
        product = dict(row)
        ean = product["ean"]
        if len(ean) >= 3:
            product["ean_last3"] = ean[-3:]
        else:
            product["ean_last3"] = ean
        products.append(product)

    return jsonify(products)

@app.route("/", methods=["GET", "POST"]) #Define a route for the index page

def index():
    result = None
    error = None
    if request.method == "POST":
        ean = request.form.get("ean", "").strip() # Get the ean
        conn = get_db_connection()
        product = conn.execute("SELECT name, location FROM products WHERE ean = ?", (ean,)).fetchone()
        conn.close()
        if product:
            if len(ean) >= 3:
                ean_last3 = ean[-3:]
            else:
                ean_last3 = ean
            result = {"name": product["name"], "location": product["location"], "ean_last3": ean_last3}
        else:
            error = f"Product with EAN {ean} not found in the database."
    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)