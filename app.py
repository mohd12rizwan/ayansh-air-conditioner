import sqlite3
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

ADMIN_PASSWORD = "Ayansh@2026"

# Database Create
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

    return redirect("/?booked=success")


@app.route("/admin")
def admin():

    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Unauthorized Access"

    conn = sqlite3.connect("leads.db")

    leads = conn.execute("""
    SELECT * FROM leads
    ORDER BY id DESC
    """).fetchall()

    conn.close()

    html = """
    <h1>Ayansh Air Conditioner Leads</h1>
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

    html += "</table>"

    return html


@app.route("/download")
def download():

    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Unauthorized"

    conn = sqlite3.connect("leads.db")

    leads = conn.execute("""
    SELECT * FROM leads
    """).fetchall()

    conn.close()

    csv_data = "ID,Name,Phone,Service,Address,Problem\n"

    for row in leads:
        csv_data += ",".join(str(x) for x in row) + "\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=leads.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)