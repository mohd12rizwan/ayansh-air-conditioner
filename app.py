import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

ADMIN_PASSWORD = "Ayansh@2026"


def init_db():
    conn = sqlite3.connect("leads.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
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


init_db()


@app.route("/")
def home():
    booked = request.args.get("booked")
    return render_template("index.html", booked=booked)


@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name")
    phone = request.form.get("phone")
    service = request.form.get("service")
    address = request.form.get("address")
    problem = request.form.get("problem")

    conn = sqlite3.connect("leads.db")

    conn.execute(
        """
        INSERT INTO leads
        (name, phone, service, address, problem)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, phone, service, address, problem)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home", booked="success"))


@app.route("/admin")
def admin():

    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return """
        <h2>Admin Login Required</h2>
        <p>Use:</p>
        <a href="/admin?password=Ayansh@2026">
        Open Admin Panel
        </a>
        """

    conn = sqlite3.connect("leads.db")
    leads = conn.execute(
        "SELECT * FROM leads ORDER BY id DESC"
    ).fetchall()
    conn.close()

    html = """
    <html>
    <head>
    <title>Admin Panel</title>
    <style>
    body{
        font-family:Arial;
        padding:20px;
        background:#f5f5f5;
    }

    table{
        width:100%;
        border-collapse:collapse;
        background:white;
    }

    th{
        background:#0d6efd;
        color:white;
    }

    th,td{
        padding:10px;
        border:1px solid #ddd;
        text-align:left;
    }

    h1{
        color:#0d6efd;
    }

    .download{
        background:green;
        color:white;
        padding:10px 15px;
        text-decoration:none;
        border-radius:5px;
    }
    </style>
    </head>
    <body>
    <h1>Ayansh Air Conditioner Leads</h1>

    <a class="download"
    href="/download?password=Ayansh@2026">
    Download CSV
    </a>

    <br><br>

    <table>

    <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Phone</th>
        <th>Service</th>
        <th>Address</th>
        <th>Problem</th>
    </tr>
    """

    for lead in leads:
        html += f"""
        <tr>
            <td>{lead[0]}</td>
            <td>{lead[1]}</td>
            <td>{lead[2]}</td>
            <td>{lead[3]}</td>
            <td>{lead[4]}</td>
            <td>{lead[5]}</td>
        </tr>
        """

    html += """
    </table>
    </body>
    </html>
    """

    return html


@app.route("/download")
def download():

    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Unauthorized"

    conn = sqlite3.connect("leads.db")
    leads = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()

    csv_data = "ID,Name,Phone,Service,Address,Problem\n"

    for row in leads:
        csv_data += ",".join(str(x) for x in row) + "\n"

    return app.response_class(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment;filename=leads.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
