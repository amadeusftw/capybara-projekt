import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from app.presentation.forms import LoginForm  # Vi måste importera formuläret!

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# --- Låtsas-användare (User) ---
class User(UserMixin):
    def __init__(self, id, is_admin=False):
        self.id = id
        self.is_admin = is_admin

# --- LOGIN ROUTE ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Skapa formuläret (Detta saknades förut!)
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.admin_dashboard'))

    # 2. Använd formulärets inbyggda validering istället för request.method == 'POST'
    if form.validate_on_submit():
        password = form.password.data
        correct_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        if password == correct_password:
            user = User(id="1", is_admin=True)
            login_user(user)
            flash('Välkommen in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_bp.admin_dashboard'))
        else:
            flash('Fel lösenord. Försök igen.', 'danger')

    # 3. VIKTIGT: Skicka med "form=form" till HTML-sidan
    return render_template('auth/login.html', form=form)

# --- LOGOUT ROUTE ---
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du har loggats ut.", "info")
    return redirect(url_for("public.index"))