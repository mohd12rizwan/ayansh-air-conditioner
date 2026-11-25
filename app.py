from contextlib import closing
from html import escape as escape_html
from io import BytesIO
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect
)

from openpyxl import Workbook

app = Flask(__name__)

# =========================
# DATABASE
# =========================

def create_db():
    conn = sqlite3.connect("leads.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        service TEXT,
        address TEXT,
        problem TEXT
    )
    """)

    conn.commit()
    conn.close()

create_db()

# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return render_template("index.html")

# =========================
# FORM SUBMIT
# =========================

@app.route("/submit", methods=["POST"])
def submit():

    conn = sqlite3.connect("leads.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO leads
    (name, phone, service, address, problem)
    VALUES (?, ?, ?, ?, ?)
    """, (
        request.form["name"],
        request.form["phone"],
        request.form["service"],
        request.form["address"],
        request.form["problem"]
    ))

    conn.commit()
    conn.close()

    return """
    <html>
    <body style='font-family:Arial;text-align:center;padding:50px'>
        <h1>✅ Service Request Submitted Successfully</h1>
        <h2>Ayansh Air Conditioner Team Will Contact You Soon</h2>
        <a href="/">Go Back</a>
    </body>
    </html>
    """

# =========================
# ADMIN PANEL
# =========================

@app.route("/admin")
def admin():

    search = request.args.get("search", "").strip()

    with closing(sqlite3.connect("leads.db")) as conn:

        if search:
            data = conn.execute(
                """
      