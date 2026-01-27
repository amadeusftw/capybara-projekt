import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.data.storage import subscribers 

bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# --- 1. LOGIN RUTT ---
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input_password = request.form.get("password")
        correct_password = os.environ.get("ADMIN_PASSWORD") or "admin123"

        if input_password == correct_password:
            session["is_admin"] = True 
            flash("Välkommen Admin! Du är inloggad. 🕵️‍♂️", "success")
            return redirect(url_for("admin_bp.admin_dashboard"))
        else:
            flash(f"Fel lösenord! (Tips: Prova 'admin123')", "error")
            return redirect(url_for("admin_bp.login"))

    return render_template("login.html")

# --- 2. LOGOUT RUTT ---
@bp.route("/logout")
def logout():
    session.pop("is_admin", None)
    flash("Du har loggat ut.", "success")
    return redirect(url_for("public.index"))

# --- 3. ADMIN DASHBOARD ---
@bp.route("/", methods=["GET"])
def admin_dashboard():
    if not session.get("is_admin"):
        flash("Vänligen logga in för att se denna sida.", "error")
        return redirect(url_for("admin_bp.login"))

    search_query = request.args.get("search", "").lower()
    
    if search_query:
        filtered_data = [
            person for person in subscribers 
            if search_query in person['name'].lower() or search_query in person['email'].lower()
        ]
    else:
        filtered_data = subscribers

    return render_template("admin.html", subscribers=filtered_data)

# --- 4. NY FUNKTION: TA BORT PRENUMERANT ---
@bp.route("/delete", methods=["POST"])
def delete_subscriber():
    if not session.get("is_admin"):
        return redirect(url_for("admin_bp.login"))
        
    email_to_delete = request.form.get("email")
    
    # Vi loopar igenom listan och tar bort den som matchar email
    # (global säger att vi vill ändra den globala variabeln subscribers)
    global subscribers
    initial_count = len(subscribers)
    subscribers[:] = [p for p in subscribers if p.get('email') != email_to_delete]
    
    if len(subscribers) < initial_count:
        flash(f"Tog bort prenumerant: {email_to_delete}", "success")
    else:
        flash("Kunde inte hitta prenumeranten.", "error")
        
    return redirect(url_for("admin_bp.admin_dashboard"))