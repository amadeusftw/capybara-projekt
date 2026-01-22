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
