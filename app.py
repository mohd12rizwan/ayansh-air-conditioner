import os

from flask import Flask, render_template, request
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

@app.route("/admin")
def admin():

    conn = sqlite3.connect("leads.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM leads")
    data = cur.fetchall()

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
        html += f"""
        <tr>
        <td>{row[0]}</td>
        <td>{row[1]}</td>
        <td>{row[2]}</td>
        <td>{row[3]}</td>
        <td>{row[4]}</td>
        <td>{row[5]}</td>
        </tr>
        """

    html += "</table>"

    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)