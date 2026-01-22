#!/bin/bash
set -e

echo "### INITIALIZING CM CORP: FINAL DISNEY EDITION ###"

# 1. Städa upp (men behåll loggan om den finns)
rm -rf app/templates
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

# 3. Backend (app.py) - Exakt logik enligt krav
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
app.config['SECRET_KEY'] = 'final-fix-secret'
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
    submit = SubmitField('JAG VILL VARA MED!')

@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        # Tyst misslyckande om mailen finns
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
        flash('Hurra! Välkommen till klubben!', 'success')
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
    # Sortera senaste överst
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

# 4. Frontend Templates (FÄRGGLAD DISNEY DESIGN)
cat <<EOF > app/templates/base.html
<!doctype html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <title>CM Corp - Capybara Adventures</title>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@300;600&family=Nunito:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            /* Ljusblå himmel-bakgrund istället för bara grönt */
            background: linear-gradient(180deg, #89f7fe 0%, #66a6ff 100%);
            font-family: 'Nunito', sans-serif;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }

        .container {
            background-color: #ffffff;
            width: 100%;
            max-width: 900px;
            border-radius: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
            margin-top: 20px;
            border: 8px solid #fff;
            text-align: center;
        }

        h1 {
            font-family: 'Fredoka', sans-serif;
            color: #FF6B6B;
            font-size: 3.5rem;
            margin: 0;
            text-shadow: 2px 2px 0px #ffeaa7;
        }
        
        h2 {
            font-family: 'Fredoka', sans-serif;
            color: #4ECDC4;
            font-size: 1.8rem;
            margin-top: 5px;
        }

        .grid-layout {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            margin-top: 40px;
            text-align: left;
        }
        
        .info-col {
            flex: 1;
            min-width: 300px;
            background: #f7f9fc;
            padding: 25px;
            border-radius: 20px;
            border: 3px solid #eef2f7;
        }
        
        .form-col {
            flex: 1;
            min-width: 300px;
            background: #fff9f0;
            padding: 25px;
            border-radius: 20px;
            border: 3px solid #ffeaa7;
        }

        /* Capybara Bild */
        .capy-pic {
            width: 100%;
            border-radius: 15px;
            border: 4px solid #4ECDC4;
            margin-bottom: 15px;
        }

        /* Inputs */
        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 2px solid #ddd;
            border-radius: 12px;
            font-family: 'Nunito', sans-serif;
            font-size: 1rem;
            box-sizing: border-box; /* Fixar layout-problem */
        }
        
        /* 3D Knapp */
        input[type="submit"], button {
            background-color: #FF6B6B;
            color: white;
            border: none;
            padding: 15px;
            width: 100%;
            font-size: 1.2rem;
            font-family: 'Fredoka', sans-serif;
            border-radius: 50px;
            cursor: pointer;
            border-bottom: 6px solid #c0392b; /* 3D effekt */
            margin-top: 15px;
            transition: transform 0.1s;
        }
        input[type="submit"]:active {
            transform: translateY(4px);
            border-bottom: 2px solid #c0392b;
        }

        /* GDPR Popup */
        .gdpr-box {
            position: relative;
            margin-top: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .tooltip {
            visibility: hidden;
            width: 250px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 10px;
            padding: 10px;
            position: absolute;
            z-index: 10;
            bottom: 130%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.9rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .tooltip::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #555 transparent transparent transparent;
        }
        .gdpr-box:hover .tooltip {
            visibility: visible;
            opacity: 1;
        }

        .footer {
            margin-top: 50px;
            color: #888;
            font-size: 0.9rem;
        }
        .footer img {
            max-height: 80px;
            display: block;
            margin: 0 auto 10px auto;
        }
        
        .flash {
            background: #a8e6cf; color: #1d643b;
            padding: 15px; border-radius: 10px; text-align:center;
            margin-bottom: 20px; font-weight: bold;
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
    <h2>Världens Ledande Marsvins-Experter</h2>
    
    {% with m=get_flashed_messages(with_categories=true) %}
        {% if m %}<div class="flash">{{ m[0][1] }}</div>{% endif %}
    {% endwith %}

    <div class="grid-layout">
        <div class="info-col">
            <h3 style="color:#4ECDC4; margin-top:0;">Om CM Corp</h3>
            <img src="https://upload.wikimedia.org/wikipedia/commons/e/ec/Capybara_%28Hydrochoerus_hydrochaeris%29.JPG" alt="Capybara" class="capy-pic">
            
            <p>Vi är ett oerhört seriöst företag. Vi sysslar inte med tråkiga saker som ekonomi. Vi sysslar med <strong>Capybaras</strong> (Vattensvin).</p>
            <p>Genom att fylla i formuläret här bredvid anmäler du dig till vårt exklusiva <strong>NYHETSBREV</strong>.</p>
            <p><strong>Du får veta allt om:</strong></p>
            <ul style="padding-left:20px;">
                <li>Hur man klappar dem</li>
                <li>Vad de gillar att äta</li>
                <li>Varför de är så coola</li>
            </ul>
        </div>

        <div class="form-col">
            <h3 style="color:#FF6B6B; margin-top:0; text-align:center;">Prenumerera Här! 📝</h3>
            <form method="POST">
                {{ form.hidden_tag() }}
                {{ form.first_name(placeholder="Förnamn") }}
                {{ form.last_name(placeholder="Efternamn") }}
                {{ form.email(placeholder="E-postadress") }}
                {{ form.company(placeholder="Företag") }}
                {{ form.title(placeholder="Titel") }}

                <div class="gdpr-box">
                    <div class="tooltip">Genom att du klickar i denna rutan så godkänner du att CM Corp äger dina uppgifter i all evig framtid.</div>
                    {{ form.gdpr() }} 
                    <label for="gdpr" style="cursor:help; font-weight:bold; color:#555;">Godkänn villkor (Håll musen här)</label>
                </div>

                {{ form.submit() }}
            </form>
        </div>
    </div>

    <div class="footer">
        <img src="{{ url_for('static', filename='logo.png') }}" alt="CM Corp Logo">
        <strong>All rights reserved © CM Corp</strong><br>
        Publicerad: $(date +%Y-%m-%d)
        <br><br>
        <a href="/login" style="text-decoration:none; color:#bbb;">Admin Login</a>
    </div>
</div>
{% endblock %}
EOF

cat <<EOF > app/templates/login.html
{% extends "base.html" %}
{% block content %}
<div class="container" style="max-width:400px;">
    <h2>🔐 Admin Login</h2>
    <form method="POST">
        <input type="password" name="pw" placeholder="Lösenord">
        <button>Logga In</button>
    </form>
</div>
{% endblock %}
EOF

cat <<EOF > app/templates/admin.html
{% extends "base.html" %}
{% block content %}
<div class="container">
    <h2>📋 Prenumeranter</h2>
    
    <div style="text-align:left; margin-bottom:20px;">
        <form method="GET" style="display:flex; gap:10px;">
            <input name="fname" placeholder="Sök..." style="width:auto; flex-grow:1; margin:0;">
            <button style="width:auto; margin:0; padding:10px 20px; font-size:1rem;">Sök</button>
            <a href="/admin" style="padding:10px;">Rensa</a>
        </form>
    </div>

    <table style="width:100%; text-align:left; border-collapse:collapse;">
        <tr style="background:#f1f1f1; color:#555;">
            <th style="padding:10px;">Datum</th>
            <th>Namn</th>
            <th>Email</th>
            <th>Titel</th>
            <th></th>
        </tr>
        {% for s in subs %}
        <tr style="border-bottom:1px solid #eee;">
            <td style="padding:10px;">{{ s.created_at.strftime('%Y-%m-%d') }}</td>
            <td>{{ s.first_name }} {{ s.last_name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.title }}</td>
            <td><a href="/delete/{{ s.id }}" style="color:#FF6B6B; font-weight:bold; text-decoration:none;">[Radera]</a></td>
        </tr>
        {% else %}
        <tr><td colspan="5" style="padding:20px; text-align:center;">Inga prenumeranter.</td></tr>
        {% endfor %}
    </table>
    <br>
    <a href="/logout" style="color:#888;">Logga ut</a>
</div>
{% endblock %}
EOF

git add .
git commit -m "Final Fix: Disney/Toy Story Theme V8" || true

echo "### KLART! Nu kan du köra appen. ###"