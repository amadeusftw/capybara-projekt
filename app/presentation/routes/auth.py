from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.business.services import AuthService
from app.presentation.forms import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Admin login route."""
    form = LoginForm()
    
    if form.validate_on_submit():
        user = AuthService.authenticate(form.username.data, form.password.data)
        
        if user:
            login_user(user)
            flash("Login successful! Welcome to the admin panel.", "success")
            return redirect(url_for("admin_bp.subscribers_list"))
        else:
            flash("Invalid username or password.", "error")
    
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Admin logout route."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("public.index"))
