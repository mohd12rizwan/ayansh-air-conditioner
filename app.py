import csv
import io
import os
import sqlite3

from flask import (
	Flask,
	Response,
	redirect,
	render_template_string,
	request,
	session,
	url_for,
)


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(32))
app.config["DATABASE"] = os.path.join(app.instance_path, "leads.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Ayansh@2026")

os.makedirs(app.instance_path, exist_ok=True)


def get_db():
	return sqlite3.connect(app.config["DATABASE"])


def init_db():
	with get_db() as conn:
		conn.execute(
			"""CREATE TABLE IF NOT EXISTS leads (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				phone TEXT NOT NULL,
				service TEXT NOT NULL,
				address TEXT NOT NULL,
				problem TEXT
			)"""
		)


init_db()


HOME_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ayansh Air Conditioner | AC Repair Greater Noida</title>
  <meta name="description" content="24x7 AC Repair, AC Installation, Fridge Repair, Washing Machine Repair and Geyser Repair Service in Greater Noida.">
  <meta name="keywords" content="AC Repair Greater Noida, AC Service, Fridge Repair, Washing Machine Repair, Geyser Repair">
  <meta property="og:title" content="Ayansh Air Conditioner">
  <meta property="og:description" content="24x7 AC Repair Service in Greater Noida">
  <style>
	:root{font-family:Arial,sans-serif;color:#14243a;background:#f4f8fc;scroll-behavior:smooth}
	*{box-sizing:border-box}body{margin:0}nav{height:68px;padding:0 7%;display:flex;align-items:center;justify-content:space-between;background:#fff;box-shadow:0 2px 12px #16324f18}
	.logo{font-weight:700;font-size:20px;color:#0878ce}.phone{font-weight:700;color:#14243a;text-decoration:none}
	.hero{text-align:center;padding:76px 20px 82px;color:white;background:linear-gradient(130deg,#0878ce,#064784)}
	.hero-badge{display:inline-block;padding:10px 16px;border-radius:30px;background:#ffffff20;font-size:14px}
	h1{font-size:clamp(34px,6vw,58px);margin:25px 0 12px}.hero h2{font-size:clamp(20px,3vw,28px);font-weight:500;margin:0 auto 12px;max-width:760px}.hero p{font-size:18px;margin:12px 0 28px}
	.btn{display:inline-block;margin:5px;padding:14px 22px;border-radius:8px;text-decoration:none;font-weight:bold}.call-btn{background:#fff;color:#0878ce}.whatsapp-btn{background:#20bd69;color:#fff}
	section{max-width:1100px;margin:auto;padding:55px 20px}section h2{text-align:center;font-size:32px;margin:0 0 28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:18px}.card{padding:24px;text-align:center;background:#fff;border-radius:12px;box-shadow:0 5px 20px #16324f0d}.card h3{margin:0;color:#0878ce;font-size:30px}.card p{margin:8px 0 0}
	.services{background:#fff}.service{font-weight:700;color:#18324b}.booking{max-width:720px}.booking form{display:grid;grid-template-columns:1fr 1fr;gap:14px}.booking input,.booking select,.booking textarea{width:100%;padding:13px;border:1px solid #d5e0eb;border-radius:7px;font:inherit}.booking textarea{grid-column:1/-1;min-height:100px;resize:vertical}.booking button{grid-column:1/-1;padding:14px;border:0;border-radius:7px;background:#0878ce;color:white;font-size:16px;font-weight:bold;cursor:pointer}.success{padding:13px;background:#e5f8ec;color:#176b35;border-radius:8px;text-align:center;margin-bottom:20px}
	footer{text-align:center;padding:25px;background:#102e4c;color:white}footer a{color:white}
	@media(max-width:600px){nav{padding:0 4%;font-size:14px}.logo{font-size:16px}.booking form{grid-template-columns:1fr}.booking textarea,.booking button{grid-column:auto}}
  </style>
</head>
<body>
  <nav><div class="logo">❄ Ayansh Air Conditioner</div><a class="phone" href="tel:+918279610802">📞 8279610802</a></nav>
  <header class="hero">
	<div class="hero-badge">⭐ 4.9 Rating &nbsp;|&nbsp; ✅ 24×7 Service &nbsp;|&nbsp; 🔧 Expert Technician</div>
	<h1>AC Repair Near Me in Greater Noida</h1>
	<h2>24×7 AC, Fridge, Washing Machine &amp; Geyser Repair Service</h2>
	<p>Same Day Doorstep Service</p>
	<a href="tel:+918279610802" class="btn call-btn">📞 Call Now</a>
	<a href="https://wa.me/918279610802?text=I%20Need%20Repair%20Service" class="btn whatsapp-btn">💬 WhatsApp Now</a>
  </header>
  <section>
	<h2>Our Achievement</h2>
	<div class="grid">
	  <div class="card"><h3>500+</h3><p>Happy Customers</p></div>
	  <div class="card"><h3>1000+</h3><p>Services Completed</p></div>
	  <div class="card"><h3>24×7</h3><p>Customer Support</p></div>
	  <div class="card"><h3>4.9 ⭐</h3><p>Customer Rating</p></div>
	</div>
  </section>
  <section class="services">
	<h2>Our Repair Services</h2>
	<div class="grid">
	  <div class="card service">❄️ AC Repair &amp; Installation</div>
	  <div class="card service">🧊 Fridge Repair</div>
	  <div class="card service">🧺 Washing Machine Repair</div>
	  <div class="card service">🚿 Geyser Repair</div>
	</div>
  </section>
  <section class="booking">
	<h2>Book a Repair Service</h2>
	{% if booked %}<div class="success">Thanks! Your service request has been received. We will contact you soon.</div>{% endif %}
	<form action="{{ url_for('submit') }}" method="post">
	  <input name="name" placeholder="Your name" required maxlength="100">
	  <input name="phone" type="tel" placeholder="Phone number" required maxlength="30">
	  <select name="service" required>
		<option value="" disabled selected>Select a service</option>
		<option>AC Repair / Installation</option><option>Fridge Repair</option>
		<option>Washing Machine Repair</option><option>Geyser Repair</option>
	  </select>
	  <input name="address" placeholder="Your address in Greater Noida" required maxlength="300">
	  <textarea name="problem" placeholder="Describe the issue (optional)" maxlength="1000"></textarea>
	  <button type="submit">Request a Callback</button>
	</form>
  </section>
  <footer>Ayansh Air Conditioner · Greater Noida · <a href="tel:+918279610802">8279610802</a></footer>
</body>
</html>"""


@app.route("/")
def home():
	return render_template_string(HOME_PAGE, booked=request.args.get("booked") == "success")


@app.route("/googlea0851a1e561d0215.html")
def google_verify():
	return "google-site-verification: googlea0851a1e561d0215.html"


@app.route("/robots.txt")
def robots():
	robots_txt = """User-agent: *
Allow: /
Sitemap: https://ayansh-air-conditioner-1.onrender.com/sitemap.xml
"""
	return Response(robots_txt, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
	xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>https://ayansh-air-conditioner-1.onrender.com/</loc>
   </url>
</urlset>"""
	return Response(xml, mimetype="application/xml")


@app.route("/submit", methods=["POST"])
def submit():
	fields = {
		"name": request.form.get("name", "").strip(),
		"phone": request.form.get("phone", "").strip(),
		"service": request.form.get("service", "").strip(),
		"address": request.form.get("address", "").strip(),
		"problem": request.form.get("problem", "").strip(),
	}
	if not all(fields[key] for key in ("name", "phone", "service", "address")):
		return redirect(url_for("home"))
	with get_db() as conn:
		conn.execute(
			"INSERT INTO leads (name, phone, service, address, problem) VALUES (?, ?, ?, ?, ?)",
			tuple(fields.values()),
		)
	return redirect(url_for("home", booked="success"))


ADMIN_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin · Ayansh Air Conditioner</title>
<style>body{font-family:Arial,sans-serif;padding:24px;background:#f4f7fb;color:#18324b}main{max-width:1100px;margin:auto}table{width:100%;border-collapse:collapse;background:white}th{background:#0878ce;color:white}th,td{padding:10px;border:1px solid #dce5ed;text-align:left}.download,button{display:inline-block;background:#0878ce;color:white;padding:11px 15px;border:0;border-radius:5px;text-decoration:none;cursor:pointer}input{padding:11px;margin:8px 0}</style></head>
<body><main><h1>Ayansh Air Conditioner Leads</h1>{% if login %}<form method="post"><label>Admin password <input type="password" name="password" required></label><button>Log in</button></form>{% if error %}<p>Incorrect password.</p>{% endif %}{% else %}<a class="download" href="{{ url_for('download') }}">Download CSV</a> <a href="{{ url_for('logout') }}">Log out</a><p>{{ leads|length }} service requests</p><table><tr><th>ID</th><th>Name</th><th>Phone</th><th>Service</th><th>Address</th><th>Problem</th></tr>{% for lead in leads %}<tr>{% for item in lead %}<td>{{ item or '' }}</td>{% endfor %}</tr>{% else %}<tr><td colspan="6">No requests yet.</td></tr>{% endfor %}</table>{% endif %}</main></body></html>"""


@app.route("/admin", methods=["GET", "POST"])
def admin():
	error = False
	if request.method == "POST":
		if request.form.get("password") == ADMIN_PASSWORD:
			session["admin"] = True
			return redirect(url_for("admin"))
		error = True
	if not session.get("admin"):
		return render_template_string(ADMIN_PAGE, login=True, error=error)
	with get_db() as conn:
		leads = conn.execute(
			"SELECT id, name, phone, service, address, problem FROM leads ORDER BY id DESC"
		).fetchall()
	return render_template_string(ADMIN_PAGE, login=False, leads=leads)


@app.route("/download")
def download():
	if not session.get("admin"):
		return redirect(url_for("admin"))
	with get_db() as conn:
		leads = conn.execute(
			"SELECT id, name, phone, service, address, problem FROM leads ORDER BY id DESC"
		).fetchall()
	output = io.StringIO()
	writer = csv.writer(output)
	writer.writerow(["ID", "Name", "Phone", "Service", "Address", "Problem"])
	writer.writerows(leads)
	return Response(
		"\ufeff" + output.getvalue(),
		mimetype="text/csv; charset=utf-8",
		headers={"Content-Disposition": "attachment; filename=ayansh-leads.csv"},
	)


@app.route("/logout")
def logout():
	session.pop("admin", None)
	return redirect(url_for("admin"))


if __name__ == "__main__":
	app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
