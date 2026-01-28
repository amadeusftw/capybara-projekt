import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
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

class RegForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired(message="Fyll i namn!")])
    last_name = StringField('Efternamn', validators=[DataRequired(message="Fyll i efternamn!")])
    email = StringField('E-post', validators=[DataRequired(), Email(message="Ogiltig e-post!")])
    company = StringField('Företag', validators=[DataRequired()])
    title = StringField('Titel', validators=[DataRequired()])
    gdpr = BooleanField('Jag godkänner att CM Corp lagrar mina uppgifter', validators=[DataRequired()])
    submit = SubmitField('JAG VILL VARA MED! 🚀')

@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        if Subscriber.query.filter_by(email=form.email.data).first():
            flash('Du är redan registrerad!', 'warning')
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
            # Skicka till den dedikerade tack-sidan
            return redirect(url_for('tack'))
    return render_template('index.html', form=form)

@app.route('/tack')
def tack():
    return render_template('thank_you.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            login_user(User())
            return redirect(url_for('admin'))
        flash('Fel lösenord!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

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
    sub = Subscriber.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    flash('Prenumerant raderad.', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
