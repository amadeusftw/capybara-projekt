#!/bin/bash
set -e

# --- KONFIGURATION ---
PROJECT="." 
echo "### INITIALIZING CM CORP: CAPYBARA EDITION ###"

# 1. Mappstruktur
rm -rf app/static 2>/dev/null
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

# 3. Backend (app.py) - Uppdaterad med GDPR-fält
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
app.config['SECRET_KEY'] = 'capybara-secret-key'
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

# Formulär med GDPR
class RegForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired()])
    last_name = StringField('Efternamn', validators=[DataRequired()])
    email = StringField('E-post', validators=[DataRequired(), Email()])
    company = StringField('Företag', validators=[DataRequired()])
    title = StringField('Titel', validators=[DataRequired()])
    # GDPR Checkbox
    gdpr = BooleanField('GDPR', validators=[DataRequired()])
    submit = SubmitField('JAG VILL HA CAPYBARA-NYHETER!')

@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        if Subscriber.query.filter_by(email=form.email.data).first():
            return redirect(url_for('index')) # Tyst reload
        
        new_sub = Subscriber(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            company=form.company.data,
            title=form.title.data
        )
        db.session.add(new_sub)
        db.session.commit()
        flash('HURRA! Du är nu en del av Capybara-familjen!', 'success')
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

# 4. Frontend Templates (CAPYBARA THEME)
cat <<EOF > app/templates/base.html
<!doctype html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <title>CM Corp - Capybara Experts</title>
    <style>
        /* Bakgrundsbild på Capybara från Unsplash */
        body {
            background: url('https://images.unsplash.com/photo-1547638375-ebf04735d96d?q=80&w=2574&auto=format&fit=crop') no-repeat center center fixed;
            background-size: cover;
            font-family: 'Comic Sans MS', 'Verdana', sans-serif; /* Lekfullt typsnitt */
            margin: 0;
            padding: 0;
            color: #333;
            /* Muspekare: En liten Capybara-ikon om webbläsaren stöder det */
            cursor: url('https://cdn-icons-png.flaticon.com/32/1998/1998610.png'), auto;
        }
        .overlay {
            background-color: rgba(255, 255, 255, 0.85); /* Ljus overlay så texten syns */
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 800px;
            margin-top: 50px;
            padding: 40px;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            text-align: center;
            border: 5px solid #8BC34A; /* Capybara-grön ram */
        }
        h1 { color: #558B2F; font-size: 3rem; margin-bottom: 10px; }
        h2 { color: #FF9800; }
        p { font-size: 1.1rem; line-height: 1.6; }
        
        input {
            width: 80%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #AED581;
            border-radius: 10px;
            font-size: 1rem;
        }
        button, input[type="submit"] {
            background-color: #FF9800;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.2rem;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover, input[type="submit"]:hover {
            transform: scale(1.05);
            background-color: #F57C00;
        }

        /* GDPR Tooltip & Styling */
        .gdpr-container {
            margin: 20px 0;
            position: relative;
            display: inline-block;
        }
        .gdpr-tooltip {
            visibility: hidden;
            width: 300px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Placera ovanför */
            left: 50%;
            margin-left: -150px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.9rem;
            pointer-events: none;
        }
        .gdpr-container:hover .gdpr-tooltip {
            visibility: visible;
            opacity: 1;
        }

        .flash { background: #DCEDC8; color: #33691E; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        
        .footer {
            margin-top: 50px;
            padding: 20px;
            font-size: 0.9rem;
            color: #555;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .footer img {
            max-width: 150px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="overlay">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
EOF

cat <<EOF > app/templates/index.html
{% extends "base.html" %}
{% block content %}
<div class="container">
    <h1>CM CORP 🥔</h1>
    <h2>Världsledande inom Capybara Excellence</h2>
    
    {% with m=get_flashed_messages(with_categories=true) %}
        {% if m %}<div class="flash">{{ m[0][1] }}</div>{% endif %}
    {% endwith %}

    <div style="text-align: left; margin-bottom: 30px;">
        <p><strong>Vilka är vi?</strong><br>
        CM Corp är ett mycket seriöst företag. Vi ägnar oss inte åt aktier, fastigheter eller krypto. Vi ägnar oss uteslutande åt <em>Hydrochoerus hydrochaeris</em> – det majestätiska vattensvinet.</p>
        
        <p><strong>Varför registrera sig?</strong><br>
        Fyller du i formuläret nedan får du exklusiv tillgång till vårt nyhetsbrev. Det innehåller allt från "Veckans Vattensvin" till tips på hur man bäst kliar en Capybara bakom örat.</p>
    </div>

    <form method="POST">
        {{ form.hidden_tag() }}
        {{ form.first_name(placeholder="Ditt förnamn") }}
        {{ form.last_name(placeholder="Ditt efternamn") }}
        {{ form.email(placeholder="Din bästa e-post") }}
        {{ form.company(placeholder="Ditt företag (eller Capybara-klubb)") }}
        {{ form.title(placeholder="Din titel (t.ex. Gnagare-entusiast)") }}

        <div class="gdpr-container">
            <span class="gdpr-tooltip">Genom att du klickar i denna rutan så godkänner du att CM Corp äger dina uppgifter i all evig framtid.</span>
            {{ form.gdpr() }} <label for="gdpr" style="cursor:help;">Jag godkänner villkoren (Håll musen här!)</label>
        </div>

        {{ form.submit() }}
    </form>
    
    <a href="/login" style="display:block; margin-top:20px; color:#aaa; font-size:0.8rem;">Admin Login</a>
</div>

<div class="footer">
    <img src="{{ url_for('static', filename='logo.png') }}" alt="CM Corp Logo">
    <div>
        <strong>All rights reserved © CM Corp</strong><br>
        Publicerad: $(date +%Y-%m-%d)
    </div>
</div>
{% endblock %}
EOF

cat <<EOF > app/templates/login.html
{% extends "base.html" %}
{% block content %}
<div class="container" style="max-width: 400px;">
    <h2>Admin Login</h2>
    <form method="POST">
        <input type="password" name="pw" placeholder="Hemligt lösenord">
        <button>Logga in</button>
    </form>
</div>
{% endblock %}
EOF

cat <<EOF > app/templates/admin.html
{% extends "base.html" %}
{% block content %}
<div class="container" style="max-width: 900px;">
    <h2>Capybara Prenumeranter</h2>
    
    <form method="GET" style="margin-bottom: 20px;">
        <input name="fname" placeholder="Sök..." style="width: 200px; display:inline;">
        <button style="padding: 10px 20px; font-size: 1rem;">Sök</button>
        <a href="/admin" style="margin-left:10px;">Rensa</a>
    </form>

    <table style="width:100%; text-align:left; border-collapse: collapse;">
        <tr style="background:#F1F8E9;">
            <th style="padding:10px;">Datum</th>
            <th>Namn</th>
            <th>Email</th>
            <th>Titel</th>
            <th></th>
        </tr>
        {% for s in subs %}
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding:10px;">{{ s.created_at.strftime('%Y-%m-%d') }}</td>
            <td>{{ s.first_name }} {{ s.last_name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.title }}</td>
            <td><a href="/delete/{{ s.id }}" style="color:red; font-weight:bold;">[X]</a></td>
        </tr>
        {% else %}
        <tr><td colspan="5" style="text-align:center;">Inga prenumeranter ännu.</td></tr>
        {% endfor %}
    </table>
    <br>
    <a href="/logout">Logga ut</a>
</div>
{% endblock %}
EOF

# Placeholder för logo om den saknas
touch app/static/logo.png

git init 2>/dev/null || true
git add .
git commit -m "Updated: CM Corp Capybara Edition V5" || true

echo "### DONE! Dags att lägga in din logga! ###"