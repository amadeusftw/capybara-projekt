import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_login import login_required

# 1. Importera verktyg och modeller
from app.extensions import db, login_manager
from app.models import Subscriber, User

load_dotenv()

# 2. SKAPA APPEN
app = Flask(__name__, template_folder='templates', static_folder='static')

# 3. Konfiguration
app.config['SECRET_KEY'] = 'hemlig-nyckel-123'
default_db_path = os.path.join(os.path.expanduser('~'), 'cm_corp.db')
db_path = os.environ.get('DATABASE_PATH', default_db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 4. Initiera verktygen
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# --- FILTER ---
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ""
    return value.strftime(format)

# --- USER LOADER ---
@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return User(id="1", is_admin=True)
    return None

# --- VALIDATOR: STOPPA Å, Ä, Ö (Endast för email nu) ---
def check_swedish_chars(form, field):
    # Kollar om fältet innehåller å, ä eller ö
    if field.data:
        forbidden = ['å', 'ä', 'ö', 'Å', 'Ä', 'Ö']
        if any(char in field.data for char in forbidden):
            raise ValidationError('E-post får inte innehålla å, ä eller ö.')

# --- FORMS ---
class RegForm(FlaskForm):
    # Nu tillåter vi ÅÄÖ i namn, företag och titel!
    first_name = StringField('Förnamn', validators=[
        DataRequired(message="Fyll i förnamn")
    ])
    
    last_name = StringField('Efternamn', validators=[
        DataRequired(message="Fyll i efternamn")
    ])
    
    # Här ligger reglerna kvar: Både @-koll och ÅÄÖ-koll
    email = StringField('E-post', validators=[
        DataRequired(message="E-post saknas"), 
        Email(message="Ogiltig e-postadress. Du måste inkludera '@'."),
        check_swedish_chars
    ])
    
    company = StringField('Företag', validators=[
        DataRequired(message="Fyll i företag")
    ])
    
    title = StringField('Titel', validators=[
        DataRequired(message="Fyll i titel")
    ])
    
    gdpr = BooleanField('Godkänn GDPR', validators=[
        DataRequired(message="Du måste godkänna GDPR-villkoren för att registrera dig.")
    ])
    
    submit = SubmitField('Skicka!')

# --- ROUTES ---
@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    
    if form.validate_on_submit():
        if Subscriber.query.filter_by(email=form.email.data).first():
            flash('Redan registrerad!', 'warning')
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
            return redirect(url_for('tack'))
    
    return render_template('index.html', form=form)

@app.route('/tack')
def tack():
    return render_template('thank_you.html')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    sub = Subscriber.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    flash('Raderad.', 'success')
    return redirect(url_for('admin_bp.admin_dashboard'))

# --- SETUP ---
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

def init_db():
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"DB Error: {e}")

init_db()

def register_blueprints():
    from app.presentation.routes.public import bp as public_bp
    from app.presentation.routes.admin import bp as admin_bp
    from app.presentation.routes.auth import auth_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

register_blueprints()

if __name__ == '__main__':
    app.run(debug=True)