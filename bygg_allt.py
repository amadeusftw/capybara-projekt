import os

print("### LÄGGER TILL STRÄNG VALIDERING I CM CORP... ###")

# 1. Säkerställ att mappar finns
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)

# 2. Skapa requirements.txt
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("Flask==3.0.0\nFlask-SQLAlchemy==3.1.1\nFlask-WTF==1.2.1\nFlask-Login==0.6.3\nemail_validator\ngunicorn")

# 3. Skapa app.py (NU MED SKARPA REGLER & FELMEDDELANDEN)
app_code = """import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hemlig-nyckel-123'
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

class User(UserMixin):
    id = 1

@login_manager.user_loader
def load_user(id):
    return User()

# HÄR ÄR ÄNDRINGEN: Custom messages för validering
class RegForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired(message="Du måste fylla i ditt förnamn!")])
    last_name = StringField('Efternamn', validators=[DataRequired(message="Du måste fylla i ditt efternamn!")])
    
    # Validering för E-post och @-tecken
    email = StringField('E-post', validators=[
        DataRequired(message="E-post är obligatoriskt!"),
        Email(message="Ogiltig e-post! Har du glömt @-tecknet?")
    ])
    
    company = StringField('Företag', validators=[DataRequired(message="Vilket företag jobbar du på?")])
    title = StringField('Titel', validators=[DataRequired(message="Vad är din titel?")])
    
    gdpr = BooleanField('GDPR', validators=[DataRequired(message="Du måste godkänna att vi äger din själ (GDPR)!")])
    submit = SubmitField('JAG VILL VARA MED!')

@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        if Subscriber.query.filter_by(email=form.email.data).first():
            flash('Du är redan med i klubben!', 'warning')
        else:
            new_sub = Subscriber(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                company=form.company.data,
                title=form.title.data
            )
            db.session.add(new_sub)
            db.session.commit()
            flash('Välkommen till Capybara-familjen! 🐾', 'success')
            return redirect(url_for('index'))
    
    # HÄR ÄR ÄNDRINGEN: Fånga upp fel om formuläret inte är giltigt
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                # Visa felet för användaren
                flash(error, 'warning')

    return render_template('index.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        pw = request.form.get('password')
        if pw == 'admin123':
            login_user(User())
            return redirect('/admin')
        flash('Fel lösenord!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/admin')
@login_required
def admin():
    search_query = request.args.get('q')
    if search_query:
        term = f"%{search_query}%"
        subs = Subscriber.query.filter(
            (Subscriber.first_name.like(term)) | 
            (Subscriber.last_name.like(term)) |
            (Subscriber.email.like(term)) | 
            (Subscriber.company.like(term))
        ).all()
    else:
        subs = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    
    return render_template('admin.html', subs=subs)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete = Subscriber.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('Prenumerant raderad.', 'info')
    return redirect('/admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
"""
with open("app/app.py", "w", encoding="utf-8") as f: f.write(app_code)

# 4. Skapa base.html (Oförändrad design)
base_html = """<!doctype html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <title>CM Corp - Capybara Magic</title>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@300;600&family=Nunito:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
            font-family: "Nunito", sans-serif; 
            margin: 0; 
            padding: 20px; 
            min-height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: flex-start;
            cursor: url('/static/cursor.png'), auto; 
        }
        .container { background-color: rgba(255, 255, 255, 0.95); width: 100%; max-width: 950px; border-radius: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); padding: 40px; margin-top: 20px; border: 6px solid #fff; text-align: center; }
        .container-admin { max-width: 1200px; }
        h1 { font-family: "Fredoka", sans-serif; color: #FF6B6B; font-size: 4rem; margin: 0; text-shadow: 3px 3px 0px #ffeaa7; letter-spacing: 2px; }
        h2 { font-family: "Fredoka", sans-serif; color: #4ECDC4; font-size: 1.8rem; margin-top: 5px; margin-bottom: 40px; }
        .grid-layout { display: flex; flex-wrap: wrap; gap: 40px; text-align: left; align-items: start; }
        .info-col { flex: 1; min-width: 300px; }
        .form-col { flex: 1; min-width: 300px; background: #fff9f0; padding: 30px; border-radius: 25px; border: 4px solid #ffeaa7; box-shadow: 0 10px 20px rgba(255, 234, 167, 0.3); }
        .capy-pic { width: 100%; border-radius: 20px; border: 5px solid #4ECDC4; margin-bottom: 20px; box-shadow: 0 8px 15px rgba(78, 205, 196, 0.2); transition: transform 0.3s; }
        .capy-pic:hover { transform: scale(1.02) rotate(1deg); }
        input { width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #eee; border-radius: 15px; font-family: "Nunito", sans-serif; font-size: 1rem; box-sizing: border-box; transition: 0.3s; }
        input:focus { border-color: #FF6B6B; outline: none; background: #fff5f5; }
        .btn-submit { background-color: #FF6B6B; color: white; border: none; padding: 15px; width: 100%; font-size: 1.3rem; font-family: "Fredoka", sans-serif; border-radius: 50px; cursor: pointer; border-bottom: 6px solid #c0392b; margin-top: 20px; transition: 0.1s; }
        .btn-submit:active { transform: translateY(4px); border-bottom: 2px solid #c0392b; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        th { text-align: left; padding: 18px; background: #4ECDC4; color: white; font-family: "Fredoka", sans-serif; font-size: 1.1rem; }
        td { padding: 15px; border-bottom: 1px solid #eee; color: #555; vertical-align: middle; text-align: left; }
        tr:last-child td { border-bottom: none; }
        tr:hover { background-color: #f9f9f9; }
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }
        .search-input { width: 60%; padding: 12px; border: 2px solid #ddd; border-radius: 50px; font-size: 1rem; }
        .search-btn { background: #555; color: white; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-weight: bold; }
        .gdpr-box { position: relative; margin-top: 15px; display: inline-block; }
        .gdpr-label { cursor: help; font-weight: bold; color: #555; text-decoration: underline; text-decoration-style: dotted; }
        .gdpr-popup-text { visibility: hidden; width: 220px; background-color: #333; color: #fff; text-align: center; border-radius: 8px; padding: 10px; position: absolute; z-index: 100; bottom: 125%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 0.8rem; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .gdpr-popup-text::after { content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #333 transparent transparent transparent; }
        .gdpr-box:hover .gdpr-popup-text { visibility: visible; opacity: 1; }
        .footer { margin-top: 60px; color: #999; font-size: 0.9rem; }
        .footer img { height: 60px; display: block; margin: 0 auto 15px auto; opacity: 0.8; }
        .flash { background: #d4edda; color: #155724; padding: 15px; border-radius: 12px; margin-bottom: 20px; font-weight: bold; border: 2px solid #c3e6cb; }
        .flash.warning { background: #fff3cd; color: #856404; border-color: #ffeeba; }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>"""
with open("app/templates/base.html", "w", encoding="utf-8") as f: f.write(base_html)

# 5. Skapa index.html (Oförändrad design)
index_html = """{% extends "base.html" %}
{% block content %}
<div class="container">
    <h1>CM CORP</h1>
    <h2>✨ Världens Ledande Marsvins-Experter ✨</h2>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <div class="grid-layout">
        <div class="info-col">
            <img src="/static/capybara.gif" alt="Dansande Capybara" class="capy-pic">
            <h3 style="color:#4ECDC4; font-family:'Fredoka'; font-size:1.5rem;">Om Vårt Nyhetsbrev 📰</h3>
            <p>Du har hittat till internets viktigaste plats. Genom att anmäla dig till vårt <strong>Nyhetsbrev</strong> får du tillgång till exklusiv information om Capybaras.</p>
            <p>I nyhetsbrevet får du varje vecka:</p>
            <ul style="color:#555; line-height: 1.6;">
                <li>🐹 Söta bilder på marsvin</li>
                <li>🛁 Tips på hur man bygger spa för gnagare</li>
                <li>👑 VIP-inbjudningar till våra träffar</li>
            </ul>
        </div>

        <div class="form-col">
            <h3 style="color:#FF6B6B; margin-top:0; font-family:'Fredoka'; text-align:center;">Prenumerera på Nyhetsbrevet! 📝</h3>
            <form method="POST">
                {{ form.hidden_tag() }}
                {{ form.first_name(placeholder="Förnamn") }}
                {{ form.last_name(placeholder="Efternamn") }}
                {{ form.email(placeholder="Din e-postadress") }}
                {{ form.company(placeholder="Företag") }}
                {{ form.title(placeholder="Titel") }}

                <div class="gdpr-box">
                    <span class="gdpr-popup-text">CM Corp kommer att äga informationen du fyller i för all evig framtid! 😈</span>
                    {{ form.gdpr() }} 
                    <label class="gdpr-label">Jag godkänner villkoren (Håll musen här)</label>
                </div>

                {{ form.submit(class="btn-submit") }}
            </form>
        </div>
    </div>

    <div class="footer">
        <img src="/static/logo.png" alt="CM Corp Logo">
        <strong>© 2024 CM Corp - All Rights Reserved</strong><br>
        <br>
        <a href="/login" style="text-decoration:none; color:#bbb; font-size:0.8rem;">Hemlig Admin Login 🔐</a>
    </div>
</div>
{% endblock %}"""
with open("app/templates/index.html", "w", encoding="utf-8") as f: f.write(index_html)

# 6. Skapa login.html
login_html = """{% extends "base.html" %}
{% block content %}
<div class="container" style="max-width:400px;">
    <h2>🔐 Endast för Chefer</h2>
    {% with messages = get_flashed_messages() %}
        {% if messages %}<div class="flash warning">{{ messages[0] }}</div>{% endif %}
    {% endwith %}
    <form method="POST">
        <input type="password" name="password" placeholder="Hemligt lösenord..." required>
        <button class="btn-submit">Logga In</button>
    </form>
    <br>
    <a href="/" style="color:#888; text-decoration:none;">← Tillbaka</a>
</div>
{% endblock %}"""
with open("app/templates/login.html", "w", encoding="utf-8") as f: f.write(login_html)

# 7. Skapa admin.html (Oförändrad med filtrering)
admin_html = """{% extends "base.html" %}
{% block content %}
<div class="container container-admin">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <h2>📋 Alla Prenumeranter</h2>
        <a href="/logout" style="background:#eee; padding:10px 20px; border-radius:20px; text-decoration:none; color:#333; font-weight:bold;">Logga ut 🏃</a>
    </div>

    {% with messages = get_flashed_messages() %}
        {% if messages %}<div class="flash">{{ messages[0] }}</div>{% endif %}
    {% endwith %}

    <div class="form-col" style="background:white; padding:20px; margin-bottom:30px; border:2px solid #eee; box-shadow:none;">
        <form method="GET" action="/admin" class="search-box" style="margin:0;">
            <input type="text" name="q" placeholder="🔎 Sök på namn, företag eller mail..." class="search-input" value="{{ request.args.get('q', '') }}">
            <button type="submit" class="search-btn">Filtrera</button>
            {% if request.args.get('q') %}
                <a href="/admin" style="padding:12px; color:#FF6B6B; text-decoration:none; display:flex; align-items:center;">Rensa X</a>
            {% endif %}
        </form>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width:20%;">Namn</th>
                <th style="width:25%;">Email</th>
                <th style="width:20%;">Företag</th>
                <th style="width:20%;">Titel</th>
                <th style="width:15%; text-align:center;">Åtgärd</th>
            </tr>
        </thead>
        <tbody>
            {% for s in subs %}
            <tr>
                <td><strong>{{ s.first_name }} {{ s.last_name }}</strong></td>
                <td>{{ s.email }}</td>
                <td>{{ s.company }}</td>
                <td>{{ s.title }}</td>
                <td style="text-align:center;">
                    <a href="/delete/{{ s.id }}" style="background:#FF6B6B; color:white; padding:5px 15px; border-radius:15px; text-decoration:none; font-size:0.9rem;" onclick="return confirm('Är du säker på att du vill radera denna?');">Radera</a>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="5" style="text-align:center; padding:30px; color:#999;">
                    {% if request.args.get('q') %}
                        Inga träffar på din sökning... 🕵️
                    {% else %}
                        Inga medlemmar registrerade än...
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}"""
with open("app/templates/admin.html", "w", encoding="utf-8") as f: f.write(admin_html)

print("### KLART! Alla fält är nu OBLIGATORISKA och @-tecken krävs. ###")