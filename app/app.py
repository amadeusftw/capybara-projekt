import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cm-corp-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cm_corp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Databasmodell
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

# Formulär (Ingen GDPR-ruta)
class RegForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired()])
    last_name = StringField('Efternamn', validators=[DataRequired()])
    email = StringField('E-post', validators=[DataRequired(), Email()])
    company = StringField('Företag', validators=[DataRequired()])
    title = StringField('Titel', validators=[DataRequired()])
    submit = SubmitField('PRENUMERERA PÅ NYHETSBREV')

@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        # KRAV: Inget felmeddelande om det misslyckas.
        # Vi kollar om mailen finns, om ja -> gör ingenting, ladda bara om.
        if Subscriber.query.filter_by(email=form.email.data).first():
            return redirect(url_for('index')) 
        
        # Om den inte finns -> Spara
        new_sub = Subscriber(
            first_name
