import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email
from flask_login import login_required

# 1. Importera verktyg och modeller
from app.extensions import db, login_manager
from app.models import Subscriber, User

load_dotenv()

# 2. SKAPA APPEN (Detta måste ske innan du använder @app...)
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

# --- HÄR (efter att app är skapad) KAN VI LÄGGA FILTER ---
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

# --- FORMS ---
class RegForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired()])
    last_name = StringField('Efternamn', validators=[DataRequired()])
    email = StringField('E-post', validators=[DataRequired(), Email()])
    company = StringField('Företag', validators=[DataRequired()])
    title = StringField('Titel', validators=[DataRequired()])
    gdpr = BooleanField('Godkänn GDPR', validators=[DataRequired()])
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
    # Importera här för att undvika cirkelberoenden
    from app.presentation.routes.public import bp as public_bp
    from app.presentation.routes.admin import bp as admin_bp
    from app.presentation.routes.auth import auth_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

register_blueprints()

if __name__ == '__main__':
    app.run(debug=True)