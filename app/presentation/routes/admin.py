from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db  # HÄR ÄR NYCKELN TILL LÖSNINGEN

bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# --- ADMIN DASHBOARD (Här finns filtreringen!) ---
@bp.route("/", methods=["GET"])
@bp.route("", methods=["GET"])
@login_required
def admin_dashboard():
    # Vi importerar Subscriber här inne för att vara säkra
    from app.models import Subscriber

    # Hämta filter från URL:en
    first_name_filter = request.args.get("first_name", "").strip()
    last_name_filter = request.args.get("last_name", "").strip()
    title_filter = request.args.get("title", "").strip()
    sort_order = request.args.get("sort", "newest")

    query = Subscriber.query

    # Applicera filter
    if first_name_filter:
        query = query.filter(Subscriber.first_name.ilike(f"%{first_name_filter}%"))
    if last_name_filter:
        query = query.filter(Subscriber.last_name.ilike(f"%{last_name_filter}%"))
    if title_filter:
        query = query.filter(Subscriber.title.ilike(f"%{title_filter}%"))

    # Applicera sortering
    if sort_order == "first_name":
        query = query.order_by(Subscriber.first_name.asc())
    elif sort_order == "last_name":
        query = query.order_by(Subscriber.last_name.asc())
    elif sort_order == "oldest":
        query = query.order_by(Subscriber.created_at.asc())
    else:  # newest
        query = query.order_by(Subscriber.created_at.desc())

    subs = query.all()
    
    # Rendera admin.html som har filtrerings-fälten
    return render_template(
        "admin.html",
        subs=subs,
        first_name_filter=first_name_filter,
        last_name_filter=last_name_filter,
        title_filter=title_filter,
        sort_order=sort_order
    )

# --- CSV EXPORT (Valfritt, men bra att ha kvar) ---
@bp.route("/export/csv", methods=["GET"])
@login_required
def export_csv():
    import io
    import csv
    from flask import Response
    from app.models import Subscriber
    
    subs = Subscriber.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Company', 'Title'])
    
    for sub in subs:
        writer.writerow([sub.id, sub.first_name, sub.last_name, sub.email, sub.company, sub.title])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=subscribers.csv'}
    )