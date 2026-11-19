from contextlib import closing
from html import escape as escape_html
from io import BytesIO
import hmac
import os

from openpyxl import Workbook
from flask import Flask, Response, render_template, request, send_file
import sqlite3

app = Flask(__name__)

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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():

    conn = sqlite3.connect("leads.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO leads
    (name,phone,service,address,problem)
    VALUES (?,?,?,?,?)
    """,
    (
        request.form["name"],
        request.form["phone"],
        request.form["service"],
        request.form["address"],
        request.form["problem"]
    ))

    conn.commit()
    conn.close()

    return """
    <h1>✅ Service Request Submitted Successfully</h1>
    <h2>Ayansh Air Conditioner Team Will Contact You Soon</h2>
    <a href="/">Go Back</a>
    """

def check_auth(username, password):
    configured_username = os.environ.get("ADMIN_USERNAME")
    configured_password = os.environ.get("ADMIN_PASSWORD")
    return (
        configured_username is not None
        and configured_password is not None
        and hmac.compare_digest(username, configured_username)
        and hmac.compare_digest(password, configured_password)
    )

def authenticate():
    return Response(
        "Login Required",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )

@app.route("/admin")
def admin():
    if not os.environ.get("ADMIN_USERNAME") or not os.environ.get("ADMIN_PASSWORD"):
        return "Admin authentication is not configured", 503

    auth = request.authorization
    if not auth or not check_auth(auth.username or "", auth.password or ""):
        return authenticate()

    with closing(sqlite3.connect("leads.db")) as conn:
        data = conn.execute("SELECT * FROM leads").fetchall()

    html = """
    <h1>All Customer Leads</h1>
    <table border='1' cellpadding='10'>
    <tr>
    <th>ID</th>
    <th>Name</th>
    <th>Phone</th>
    <th>Service</th>
    <th>Address</th>
    <th>Problem</th>
    </tr>
    """

    for row in data:
        cells = "".join(f"<td>{escape_html(str(value))}</td>" for value in row)
        html += f"""
        <tr>
        {cells}
        </tr>
        """

    html += "</table>"

    return html

@app.route("/download")
def download():
    if not os.environ.get("ADMIN_USERNAME") or not os.environ.get("ADMIN_PASSWORD"):
        return "Admin authentication is not configured", 503

    auth = request.authorization
    if not auth or not check_auth(auth.username or "", auth.password or ""):
        return authenticate()

    conn = sqlite3.connect("leads.db")
    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet(title="Leads")
    try:
        cursor = conn.execute("SELECT * FROM leads")
        sheet.append([column[0] for column in cursor.description])
        for row in cursor:
            sheet.append(row)
    finally:
        conn.close()

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="leads.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)