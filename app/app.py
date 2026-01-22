import os
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
    # HÄR ÄR FILTRERINGS-LOGIKEN
    search_query = request.args.get('q')
    if search_query:
        # Sök i förnamn, efternamn, email eller företag
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
