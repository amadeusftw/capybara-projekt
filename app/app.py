import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'hemlig-nyckel-123'

# Use environment variable for database path; pick a sensible default per OS
default_db = '/tmp/cm_corp.db' if os.name != 'nt' else os.path.join(os.getcwd(), 'cm_corp.db')
db_path = os.environ.get('DATABASE_PATH', default_db)

# Normalize to absolute path and ensure parent directory exists so SQLite can open the file
db_path = os.path.abspath(db_path)
db_dir = os.path.dirname(db_path)
if db_dir:
    try:
        os.makedirs(db_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create database directory '{db_dir}': {e}")

# On Windows the path may contain backslashes; normalize to forward slashes for the URI
db_path = db_path.replace('\\', '/')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models defined here for backward compatibility
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    company = db.Column(db.String(100))
    title = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    """Admin user model with password authentication."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Hash and store the password."""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash."""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID for Flask-Login."""
    return User.query.get(int(user_id))

class RegForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired(message="Fyll i namn!")])
    last_name = StringField('Efternamn', validators=[DataRequired(message="Fyll i efternamn!")])
    email = StringField('E-post', validators=[DataRequired(), Email(message="Ogiltig e-post!")])
    company = StringField('Företag', validators=[DataRequired()])
    title = StringField('Titel', validators=[DataRequired()])
    gdpr = BooleanField('Jag godkänner att CM Corp lagrar mina uppgifter', validators=[DataRequired()])
    submit = SubmitField('Ja, skicka mig Capybaraaas!')

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
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        if request.form.get('password') == admin_password:
            login_user(SimpleUser())
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
    # Get filter parameters
    first_name_filter = request.args.get('first_name', '').strip()
    last_name_filter = request.args.get('last_name', '').strip()
    date_filter = request.args.get('date', '').strip()
    sort_order = request.args.get('sort', 'newest')
    
    # Start with base query
    query = Subscriber.query
    
    # Apply filters
    if first_name_filter:
        query = query.filter(Subscriber.first_name.ilike(f"%{first_name_filter}%"))
    
    if last_name_filter:
        query = query.filter(Subscriber.last_name.ilike(f"%{last_name_filter}%"))
    
    if date_filter:
        today = datetime.utcnow().date()
        
        if date_filter == 'today':
            query = query.filter(Subscriber.created_at >= datetime(today.year, today.month, today.day))
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            query = query.filter(Subscriber.created_at >= datetime(week_ago.year, week_ago.month, week_ago.day))
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            query = query.filter(Subscriber.created_at >= datetime(month_ago.year, month_ago.month, month_ago.day))
    
    # Apply sorting
    if sort_order == 'oldest':
        subs = query.order_by(Subscriber.created_at.asc()).all()
    else:  # default 'newest'
        subs = query.order_by(Subscriber.created_at.desc()).all()
    
    return render_template('admin.html', 
                         subs=subs, 
                         first_name_filter=first_name_filter,
                         last_name_filter=last_name_filter,
                         date_filter=date_filter,
                         sort_order=sort_order)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    sub = Subscriber.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    flash('Prenumerant raderad.', 'success')
    return redirect(url_for('admin'))

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Initialize database on startup
def init_db():
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

init_db()

# Register blueprints (delayed to avoid circular imports)
def register_blueprints():
    from app.presentation.routes.public import bp as public_bp
    from app.presentation.routes.admin import bp as admin_bp
    from app.presentation.routes.auth import auth_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

register_blueprints()

# CLI command for creating admin users
@app.cli.command()
def create_admin():
    """Create a new admin user from the command line (idempotent)."""
    import sys
    import click
    from app.business.services import AuthService
    from app.business.services.auth_service import DuplicateUsernameError
    
    # Interactive prompts for username and password
    username = click.prompt('Enter username', type=str)
    password = click.prompt('Enter password', type=str, hide_input=True, confirmation_prompt=True)
    
    try:
        user = AuthService.create_user(username, password)
        click.secho(f'✅ Admin user "{username}" created successfully!', fg='green')
        sys.exit(0)
        
    except DuplicateUsernameError:
        click.secho(f'ℹ️  Admin user already exists (idempotent - not an error)', fg='yellow')
        sys.exit(0)  # Exit 0 for idempotent behavior
    except Exception as e:
        click.secho(f'❌ Error creating admin user: {str(e)}', fg='red')
        sys.exit(1)

if __name__ == '__main__':
    app.run(debug=True)
