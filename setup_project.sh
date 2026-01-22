#!/bin/bash
set -e

echo "### INITIALIZING CM CORP: GALACTIC CAPYBARA EDITION ###"

# 1. Mappstruktur (VIKTIGT: Raderar INTE static-mappen nu, så din logga sparas)
mkdir -p app/{templates,static} .github/workflows infra

# 2. Python Requirements
cat <<EOF > requirements.txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
Flask-Login==0.6.3
email_validator
gunicorn
EOF

# 3. Backend (app.py) - Oförändrad logik, fungerar bra
cat <<EOF > app/app.py
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'space-capy-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cm_corp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    company = db.Column(db.String(100))
    title = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin): id=1
@login_manager.user_loader
def load_user(id): return User()

class RegForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired()])
    last_name = StringField('Efternamn', validators=[DataRequired()])
    email = StringField('E-post', validators=[DataRequired(), Email()])
    company = StringField('Företag', validators=[DataRequired()])
    title = StringField('Titel', validators=[DataRequired()])
    gdpr = BooleanField('GDPR', validators=[DataRequired()])
    submit = SubmitField('INITIERA UPPSKJUTNING 🚀')

@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        if Subscriber.query.filter_by(email=form.email.data).first():
            return redirect(url_for('index'))
        
        new_sub = Subscriber(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            company=form.company.data,
            title=form.title.data
        )
        db.session.add(new_sub)
        db.session.commit()
        flash('SUCCESS: Du är nu en Space Capybara Cadet!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST' and request.form.get('pw')=='admin123':
        login_user(User())
        return redirect('/admin')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/admin')
@login_required
def admin():
    search_fname = request.args.get('fname')
    search_lname = request.args.get('lname')
    search_email = request.args.get('email')
    query = Subscriber.query.order_by(Subscriber.created_at.desc())
    if search_fname: query = query.filter(Subscriber.first_name.contains(search_fname))
    if search_lname: query = query.filter(Subscriber.last_name.contains(search_lname))
    if search_email: query = query.filter(Subscriber.email.contains(search_email))
    return render_template('admin.html', subs=query.all())

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    db.session.delete(Subscriber.query.get(id))
    db.session.commit()
    return redirect('/admin')

if __name__=='__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
EOF

# 4. Frontend Templates (SPACE CAPYBARA THEME)
cat <<EOF > app/templates/base.html
<!doctype html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <title>CM Corp - Galactic Capybaras</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Exo+2:wght@300;600&display=swap" rel="stylesheet">
    <style>
        body {
            /* Rymdbakgrund */
            background: url('https://images.unsplash.com/photo-1444703686981-a3abbc4d4fe3?q=80&w=2600&auto=format&fit=crop') no-repeat center center fixed;
            background-size: cover;
            font-family: 'Exo 2', sans-serif;
            margin: 0;
            padding: 0;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: crosshair; /* Space-sikte istället för kossa */
        }

        /* En mörk hinna över bakgrunden för läsbarhet */
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: -1;
        }

        .container {
            width: 100%;
            max-width: 700px;
            padding: 40px;
            /* Glassmorphism effekt (genomskinligt glas) */
            background: rgba(15, 15, 25, 0.85);
            backdrop-filter: blur(10px);
            border: 2px solid #00ffcc; /* Neon-grön ram */
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0, 255, 204, 0.3);
            text-align: center;
            margin-top: 20px;
            margin-bottom: 20px;
        }

        /* Neon Glow Text */
        h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 3rem;
            margin-bottom: 10px;
            color: #fff;
            text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        }
        h2 {
            font-family: 'Orbitron', sans-serif;
            color: #b388ff; /* Neon lila */
            text-shadow: 0 0 5px #b388ff;
        }

        p { font-size: 1.1rem; line-height: 1.6; color: #e0e0e0; }

        /* Capybara Image styling */
        .capy-img {
            width: 100%;
            max-width: 500px;
            border-radius: 10px;
            border: 2px solid #b388ff;
            box-shadow: 0 0 15px rgba(179, 136, 255, 0.4);
            margin: 20px 0;
        }

        /* Inputs */
        input {
            width: 80%;
            padding: 12px;
            margin: 10px 0;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ffcc;
            color: #00ffcc;
            border-radius: 5px;
            font-family: 'Exo 2', sans-serif;
            font-size: 1rem;
        }
        input::placeholder { color: #007d64; }
        
        /* Submit Button */
        input[type="submit"], button {
            background: linear-gradient(45deg, #00ffcc, #00997a);
            color: #000;
            border: none;
            padding: 15px 40px;
            font-size: 1.2rem;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            font-family: 'Orbitron', sans-serif;
            margin-top: 20px;
            box-shadow: 0 0 15px #00ffcc;
            transition: 0.3s;
        }
        input[type="submit"]:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px #00ffcc;
        }

        /* GDPR Styling - Centrerat och Tydligt */
        .gdpr-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            position: relative;
        }
        
        .gdpr-popup {
            visibility: hidden;
            width: 250px;
            background-color: #b388ff;
            color: #000;
            text-align: center;
            border-radius: 5px;
            padding: 10px;
            position: absolute;
            bottom: 140%;
            left: 50%;
            transform: translateX(-50%);
            font-weight: bold;
            box-shadow: 0 0 10px #b388ff;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 10;
        }
        
        .gdpr-row:hover .gdpr-popup {
            visibility: visible;
            opacity: 1;
        }

        .flash {
            background: rgba(0, 255, 204, 0.2);
            border: 1px solid #00ffcc;
            color: #00ffcc;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.8rem;
            color: #666;
            width: 100%;
        }
        .footer img {
            max-width: 120px;
            filter: drop-shadow(0 0 5px #fff); /* Glow på loggan */
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
EOF

cat <<EOF > app/templates/index.html
{% extends "base.html" %}
{% block content %}
<div class="container">
    <h1>CM CORP</h1>
    <h2>INTERGALACTIC CAPYBARA DIVISION</h2>
    
    {% with m=get_flashed_messages(with_categories=true) %}
        {% if m %}<div class="flash">{{ m[0][1] }}</div>{% endif %}
    {% endwith %}

    <img src="https://images.unsplash.com/photo-1547638375-ebf04735d96d?q=80&w=1200" alt="Space Capybara" class="capy-img">

    <div style="text-align: left; margin: 20px 0;">
        <p><strong>MISSION STATUS:</strong><br>
        Välkommen till CM Corp. Vi är ett extremt seriöst företag som specialiserar oss på <em>Hydrochoerus hydrochaeris</em> i nollgravitation. Marsvin är framtiden.</p>
        
        <p><strong>PROTOCOL:</strong><br>
        Fyll i data nedan för att få access till vårt krypterade nyhetsbrev om rymd-marsvin och deras dominans i universum.</p>
    </div>

    <form method="POST">
        {{ form.hidden_tag() }}
        {{ form.first_name(placeholder="FÖRNAMN") }}
        {{ form.last_name(placeholder="EFTERNAMN") }}
        {{ form.email(placeholder="KOMMUNIKATIONS-ID (EMAIL)") }}
        {{ form.company(placeholder="BAS / FÖRETAG") }}
        {{ form.title(placeholder="RANG / TITEL") }}

        <div class="gdpr-row">
            <div class="gdpr-popup">Genom att klicka här godkänner du att CM Corp äger dina uppgifter i all evig framtid (och i hela galaxen).</div>
            {{ form.gdpr() }} 
            <label for="gdpr" style="color:#00ffcc; cursor:help;">JAG GODKÄNNER VILLKOREN</label>
        </div>

        {{ form.submit() }}
    </form>
</div>

<div class="footer">
    <img src="{{ url_for('static', filename='logo.png') }}" alt="CM Corp Logo">
    <div>
        <strong>ALL RIGHTS RESERVED © CM CORP</strong><br>
        SYSTEM DATE: $(date +%Y-%m-%d)
    </div>
    <br>
    <a href="/login" style="color:#333; text-decoration:none;">[ADMIN ACCESS]</a>
</div>
{% endblock %}
EOF

cat <<EOF > app/templates/login.html
{% extends "base.html" %}
{% block content %}
<div class="container" style="max-width: 400px;">
    <h2>ADMIN ACCESS</h2>
    <form method="POST">
        <input type="password" name="pw" placeholder="SECURITY CODE">
        <button style="width:100%;">ACCESS</button>
    </form>
</div>
{% endblock %}
EOF

cat <<EOF > app/templates/admin.html
{% extends "base.html" %}
{% block content %}
<div class="container" style="max-width: 900px;">
    <h2 style="color:#00ffcc;">DATABASE: SUBSCRIBERS</h2>
    
    <form method="GET" style="margin-bottom: 20px;">
        <input name="fname" placeholder="SEARCH QUERY..." style="width: 200px; display:inline;">
        <button style="padding: 10px 20px; font-size: 1rem; margin-top:0;">SCAN</button>
        <a href="/admin" style="margin-left:10px; color:#fff;">RESET</a>
    </form>

    <table style="width:100%; text-align:left; border-collapse: collapse; color:#ddd;">
        <tr style="border-bottom: 2px solid #00ffcc;">
            <th style="padding:10px;">TIMESTAMP</th>
            <th>IDENTITY</th>
            <th>COMM-LINK</th>
            <th>RANK</th>
            <th></th>
        </tr>
        {% for s in subs %}
        <tr style="border-bottom: 1px solid #333;">
            <td style="padding:10px;">{{ s.created_at.strftime('%Y-%m-%d') }}</td>
            <td>{{ s.first_name }} {{ s.last_name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.title }}</td>
            <td><a href="/delete/{{ s.id }}" style="color:#ff3333; font-weight:bold; text-decoration:none;">[PURGE]</a></td>
        </tr>
        {% else %}
        <tr><td colspan="5" style="text-align:center; padding:20px;">NO DATA FOUND.</td></tr>
        {% endfor %}
    </table>
    <br>
    <a href="/logout" style="color:#00ffcc;">TERMINATE SESSION</a>
</div>
{% endblock %}
EOF

# Skapar bara filen om den saknas, raderar inte existerande!
if [ ! -f app/static/logo.png ]; then
    touch app/static/logo.png
fi

git add .
git commit -m "Design Overhaul: Galactic Capybara V6" || true

echo "### SYSTEM READY. UPLOAD TO GITHUB. ###"