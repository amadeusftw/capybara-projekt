from flask import Blueprint, render_template, request
from app.data.storage import subscribers # Vi importerar listan för att kunna spara i den

bp = Blueprint("public", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/subscribe")
def subscribe():
    """Render the subscription form."""
    return render_template("subscribe.html")

@bp.route("/subscribe/confirm", methods=["POST"])
def subscribe_confirm():
    """Handle subscription form submission."""
    # 1. Hämta all data (nu 4 fält)
    email = request.form.get("email")
    name = request.form.get("name")
    company = request.form.get("company")
    title = request.form.get("title")

    # 2. SPARA i vår lista (så admin kan se det)
    # I en riktig app hade detta sparats i en databas
    new_subscriber = {
        "name": name,
        "email": email,
        "company": company,
        "title": title
    }
    subscribers.append(new_subscriber)

    # 3. Visa tack-sidan
    return render_template("thank_you.html", email=email, name=name)