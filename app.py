from contextlib import closing
from html import escape as escape_html
from io import BytesIO
import sqlite3
import os
import hmac

from flask import (
    Flask,
    render_template,
    request,
    Response,
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
# FORM SUBMISSION
# =========================

@app.route("/submit", methods=["POST"])
def submit():

    conn = sqlite3.connect("leads.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO leads
    (name, phone, service, address, problem)
    VALUES (?, ?, ?, ?, ?)
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
    <html>
    <body style='font-family:Arial;text-align:center;padding:50px'>
        <h1>✅ Service Request Submitted Successfully</h1>
        <h2>Ayansh Air Conditioner Team Will Contact You Soon</h2>
        <a href='/'>Go Back</a>
    </body>
    </html>
    """


# =========================
# ADMIN AUTH
# =========================

def check_auth(username, password):

    admin_user = os.environ.get("ADMIN_USERNAME")
    admin_pass = os.environ.get("ADMIN_PASSWORD")

    return (
        admin_user is not None
        and admin_pass is not None
        and hmac.compare_digest(username, admin_user)
        and hmac.compare_digest(password, admin_pass)
    )


def authenticate():
    return Response(
        "Admin Login Required",
        401,
        {"WWW-Authenticate": 'Basic realm="Admin Area"'}
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    if not os.environ.get("ADMIN_USERNAME") or not os.environ.get("ADMIN_PASSWORD"):
        return "Admin authentication is not configured", 503

    auth = request.authorization

    if not auth or not check_auth(auth.username or "", auth.password or ""):
        return authenticate()

    search = request.args.get("search", "").strip()

    with closing(sqlite3.connect("leads.db")) as conn:

        if search:
            data = conn.execute(
                """
                SELECT * FROM leads
                WHERE name LIKE ?
                OR phone LIKE ?
                """,
                (f"%{search}%", f"%{search}%")
            ).fetchall()
        else:
            data = conn.execute(
                "SELECT * FROM leads ORDER BY id DESC"
            ).fetchall()

    total_leads = len(data)

    html = f"""
    <html>
    <head>
        <title>Ayansh Admin Panel</title>

        <style>

            body {{
                font-family: Arial;
                margin: 25px;
                background: #f4f6f9;
            }}

            h1 {{
                color: #2563eb;
            }}

            .card {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,.08);
            }}

            table {{
                width:100%;
                border-collapse:collapse;
                background:white;
            }}

            th {{
                background:#2563eb;
                color:white;
            }}

            th, td {{
                padding:12px;
                border:1px solid #ddd;
                text-align:left;
            }}

            .btn {{
                text-decoration:none;
                padding:10px 18px;
                border-radius:6px;
                color:white;
                margin-right:10px;
            }}

            .green {{
                background:#16a34a;
            }}

            .red {{
                background:#dc2626;
            }}

            input {{
                padding:10px;
                width:250px;
            }}

            button {{
                padding:10px 15px;
                background:#2563eb;
                color:white;
                border:none;
                cursor:pointer;
            }}

        </style>

    </head>

    <body>

        <div class="card">
            <h1>Ayansh Air Conditioner Admin Panel</h1>
            <h2>Total Leads: {total_leads}</h2>

            <a class="btn green" href="/download">
                Download Excel
            </a>
        </div>

        <div class="card">

            <form method="get">

                <input
                    type="text"
                    name="search"
                    placeholder="Search Name or Phone"
                    value="{escape_html(search)}"
                >

                <button type="submit">
                    Search
                </button>

            </form>

        </div>

        <table>

            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Service</th>
                <th>Address</th>
                <th>Problem</th>
                <th>Action</th>
            </tr>
    """

    for row in data:

        id_, name, phone, service, address, problem = row

        html += f"""
        <tr>

            <td>{id_}</td>

            <td>{escape_html(str(name))}</td>

            <td>{escape_html(str(phone))}</td>

            <td>{escape_html(str(service))}</td>

            <td>{escape_html(str(address))}</td>

            <td>{escape_html(str(problem))}</td>

            <td>
                <a class="btn red"
                   href="/delete/{id_}"
                   onclick="return confirm('Delete this lead?')">
                   Delete
                </a>
            </td>

        </tr>
        """

    html += """
        </table>

    </body>
    </html>
    """

    return html


# =========================
# DELETE LEAD
# =========================

@app.route("/delete/<int:lead_id>")
def delete_lead(lead_id):

    auth = request.authorization

    if not auth or not check_auth(auth.username or "", auth.password or ""):
        return authenticate()

    conn = sqlite3.connect("leads.db")

    conn.execute(
        "DELETE FROM leads WHERE id=?",
        (lead_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# DOWNLOAD EXCEL
# =========================

@app.route("/download")
def download():

    auth = request.authorization

    if not auth or not check_auth(auth.username or "", auth.password or ""):
        return authenticate()

    workbook = Workbook(write_only=True)

    sheet = workbook.create_sheet("Leads")

    conn = sqlite3.connect("leads.db")

    try:

        cursor = conn.execute(
            "SELECT * FROM leads"
        )

        sheet.append(
            [col[0] for col in cursor.description]
        )

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
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)