# ============================================
# PHANTOM ROLEPLAY - Server Website
# BY MANINI
# ============================================

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'phantom_secret_key_2026'
DB = 'phantom.db'

# ============================================
# 🔔 Discord Webhooks
# ============================================
WEBHOOK_ACCEPTED = 'https://discord.com/api/webhooks/1557423244238131311/0Y_YOaauJ6xoQpIoS9jUjBsTf6fgiYbW0z43CpDpX7oTQjoXU60j6v-fzq0dnyP1Dwec'
WEBHOOK_REFUSED  = 'https://discord.com/api/webhooks/1557423664499265639/UWlElWWMXHYqCyzxmTbADA62uOJvpcu5O52WaXRfonxxPxoNZH69iaK5HsDyspEj07rO'
WEBHOOK_NEW      = 'https://discord.com/api/webhooks/1557431944109756568/MmJycPOWKHmxyXc5BfuvwfVZiBH1X4fS84fTxS4C3ok_dRFBgjR-Mli6U70nr3JlIQ7S'


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admin_apps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, age INTEGER, discord TEXT,
        experience TEXT, hours INTEGER,
        status TEXT DEFAULT 'pending', created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS whitelist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingame_name TEXT NOT NULL, email TEXT NOT NULL,
        discord TEXT, age INTEGER, why TEXT,
        status TEXT DEFAULT 'pending', created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS vip_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL,
        package TEXT NOT NULL, price INTEGER,
        status TEXT DEFAULT 'pending', created_at TEXT
    )''')
    conn.commit()
    conn.close()


init_db()


# ============================================
# إرسال قبول / رفض
# ============================================
def send_to_discord(webhook_url, data, action):
    if not webhook_url:
        return
    try:
        is_accepted = action == 'accepted'
        embed = {
            "title": "✅ WHITELIST ACCEPTED" if is_accepted else "❌ WHITELIST REFUSED",
            "color": 0x22c55e if is_accepted else 0xef4444,
            "fields": [
                {"name": "👤 In-Game Name", "value": str(data[1]), "inline": True},
                {"name": "🎂 Age", "value": str(data[4]), "inline": True},
                {"name": "📧 Email", "value": str(data[2]), "inline": True},
                {"name": "💬 Discord", "value": str(data[3]), "inline": True},
                {"name": "📝 Why Join", "value": (str(data[5])[:300] if data[5] else "N/A"), "inline": False},
                {"name": "📅 Applied At", "value": str(data[7]), "inline": False}
            ],
            "footer": {"text": "PHANTOM ROLEPLAY • Whitelist System"}
        }
        requests.post(webhook_url, json={"embeds": [embed]}, timeout=5)
    except Exception as e:
        print(f"[Discord Error] {e}")


# ============================================
# إرسال طلب جديد
# ============================================
def send_new_application(webhook_url, wid, ingame_name, email, discord, age, why):
    if not webhook_url:
        return
    try:
        embed = {
            "title": "📥 NEW WHITELIST APPLICATION",
            "color": 0xffaa00,
            "fields": [
                {"name": "🆔 Application ID", "value": f"#{wid}", "inline": True},
                {"name": "👤 In-Game Name", "value": str(ingame_name), "inline": True},
                {"name": "🎂 Age", "value": str(age), "inline": True},
                {"name": "📧 Email", "value": str(email), "inline": True},
                {"name": "💬 Discord", "value": str(discord), "inline": True},
                {"name": "📝 Why Join", "value": (str(why)[:300] if why else "N/A"), "inline": False}
            ],
            "footer": {"text": "PHANTOM ROLEPLAY • New Application"}
        }
        requests.post(webhook_url, json={"embeds": [embed]}, timeout=5)
    except Exception as e:
        print(f"[Discord Error] {e}")


# ============================================
# الصفحات
# ============================================
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/rules')
def rules():
    return render_template('rules.html')


@app.route('/apply-admin', methods=['GET', 'POST'])
def apply_admin():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        discord = request.form['discord']
        experience = request.form['experience']
        hours = int(request.form['hours'])
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO admin_apps (name, age, discord, experience, hours, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, age, discord, experience, hours, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
        flash('Application sent!', 'success')
        return redirect(url_for('apply_admin'))
    return render_template('apply_admin.html')


@app.route('/whitelist', methods=['GET', 'POST'])
def whitelist():
    if request.method == 'POST':
        ingame_name = request.form['ingame_name']
        email = request.form['email']
        discord = request.form['discord']
        age = int(request.form['age'])
        why = request.form['why']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO whitelist (ingame_name, email, discord, age, why, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (ingame_name, email, discord, age, why, datetime.now().strftime("%Y-%m-%d %H:%M")))
        wid = c.lastrowid
        conn.commit()
        conn.close()

        # إشعار طلب جديد
        send_new_application(WEBHOOK_NEW, wid, ingame_name, email, discord, age, why)

        flash('Whitelist application sent!', 'success')
        return redirect(url_for('whitelist'))
    return render_template('whitelist.html')


@app.route('/vip', methods=['GET', 'POST'])
def vip():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        package = request.form['package']
        price = int(request.form['price'])
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO vip_requests (name, email, package, price, created_at) VALUES (?, ?, ?, ?, ?)",
                  (name, email, package, price, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
        flash(f'VIP {package} request sent!', 'success')
        return redirect(url_for('vip'))
    return render_template('vip.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['password'] == 'phantom2026':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Wrong password!', 'danger')

    if not session.get('admin'):
        return render_template('admin_login.html')

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM admin_apps ORDER BY id DESC")
    admin_apps = c.fetchall()
    c.execute("SELECT * FROM whitelist ORDER BY id DESC")
    whitelist_apps = c.fetchall()
    c.execute("SELECT * FROM vip_requests ORDER BY id DESC")
    vip_requests = c.fetchall()
    conn.close()
    return render_template('admin.html', admin_apps=admin_apps, whitelist_apps=whitelist_apps, vip_requests=vip_requests)


@app.route('/admin/whitelist/<int:wid>/<action>')
def whitelist_action(wid, action):
    if not session.get('admin'):
        return redirect(url_for('admin'))

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM whitelist WHERE id=?", (wid,))
    data = c.fetchone()

    if not data:
        conn.close()
        flash('Application not found!', 'danger')
        return redirect(url_for('admin'))

    new_status = 'accepted' if action == 'accept' else 'refused'
    c.execute("UPDATE whitelist SET status=? WHERE id=?", (new_status, wid))
    conn.commit()
    conn.close()

    if action == 'accept':
        send_to_discord(WEBHOOK_ACCEPTED, data, 'accepted')
    else:
        send_to_discord(WEBHOOK_REFUSED, data, 'refused')

    flash(f'Application {new_status}!', 'success')
    return redirect(url_for('admin'))


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
