from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "leadmaster_super_secret_key"

DATABASE = "database.db"


# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        business TEXT,
        status TEXT DEFAULT 'חדש',
        notes TEXT DEFAULT '',
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        hero_title TEXT,
        hero_subtitle TEXT,
        whatsapp TEXT,
        email TEXT
    )
    """)

    cur.execute("""
    SELECT * FROM settings WHERE id=1
    """)

    existing = cur.fetchone()

    if not existing:
        cur.execute("""
        INSERT INTO settings
        (id, hero_title, hero_subtitle, whatsapp, email)
        VALUES
        (
            1,
            'לידים איכותיים לעסק שלך',
            'LeadMaster - סוכנות לידים ובינה מלאכותית',
            '972500000000',
            'info@leadmaster.co.il'
        )
        """)

    conn.commit()
    conn.close()


# =========================
# GOOGLE VERIFICATION
# =========================

@app.route('/googleec85de9a6bf4c91c.html')
def google_verify():
    return app.send_static_file('googleec85de9a6bf4c91c.html')


# =========================
# SITEMAP
# =========================

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')


# =========================
# ROBOTS
# =========================

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    conn = get_db()

    settings = conn.execute(
        "SELECT * FROM settings WHERE id=1"
    ).fetchone()

    conn.close()

    return render_template(
        "index.html",
        settings=settings
    )


# =========================
# LEAD FORM
# =========================

@app.route("/submit-lead", methods=["POST"])
def submit_lead():

    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    business = request.form.get("business")

    conn = get_db()

    conn.execute("""
    INSERT INTO leads
    (
        name,
        phone,
        email,
        business,
        created_at
    )
    VALUES
    (?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        business,
        datetime.now().strftime("%d/%m/%Y %H:%M")
    ))

    conn.commit()
    conn.close()

    flash("הפרטים נשלחו בהצלחה")

    return redirect("/")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "ggpac200s" and password == "301805172sY!":

            session["admin"] = True

            return redirect("/admin")

        flash("שם משתמש או סיסמה שגויים")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()

    leads = conn.execute("""
    SELECT *
    FROM leads
    ORDER BY id DESC
    """).fetchall()

    settings = conn.execute("""
    SELECT *
    FROM settings
    WHERE id=1
    """).fetchone()

    conn.close()

    return render_template(
        "admin.html",
        leads=leads,
        settings=settings
    )


# =========================
# UPDATE WEBSITE SETTINGS
# =========================

@app.route("/update-settings", methods=["POST"])
def update_settings():

    if not session.get("admin"):
        return redirect("/login")

    hero_title = request.form.get("hero_title")
    hero_subtitle = request.form.get("hero_subtitle")
    whatsapp = request.form.get("whatsapp")
    email = request.form.get("email")

    conn = get_db()

    conn.execute("""
    UPDATE settings
    SET
        hero_title=?,
        hero_subtitle=?,
        whatsapp=?,
        email=?
    WHERE id=1
    """, (
        hero_title,
        hero_subtitle,
        whatsapp,
        email
    ))

    conn.commit()
    conn.close()

    flash("האתר עודכן בהצלחה")

    return redirect("/admin")


# =========================
# DELETE LEAD
# =========================

@app.route("/delete-lead/<int:lead_id>")
def delete_lead(lead_id):

    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()

    conn.execute(
        "DELETE FROM leads WHERE id=?",
        (lead_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# UPDATE LEAD STATUS
# =========================

@app.route("/update-status/<int:lead_id>", methods=["POST"])
def update_status(lead_id):

    if not session.get("admin"):
        return redirect("/login")

    status = request.form.get("status")

    conn = get_db()

    conn.execute("""
    UPDATE leads
    SET status=?
    WHERE id=?
    """, (
        status,
        lead_id
    ))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# STARTUP
# =========================

init_db()

if __name__ == "__main__":
    app.run(debug=True)
