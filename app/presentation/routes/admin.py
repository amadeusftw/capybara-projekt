import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user

bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

## Removed legacy login route. Use /auth/login instead.

## Removed legacy logout route. Use /auth/logout instead.

# --- 3. ADMIN DASHBOARD ---
@bp.route("/", methods=["GET"])
@bp.route("", methods=["GET"])
@login_required
def admin_dashboard():
    from app.app import db, Subscriber
    # Filtrering
    first_name_filter = request.args.get("first_name", "").strip()
    last_name_filter = request.args.get("last_name", "").strip()
    title_filter = request.args.get("title", "").strip()
    sort_order = request.args.get("sort", "newest")

    query = Subscriber.query
    if first_name_filter:
        query = query.filter(Subscriber.first_name.ilike(f"%{first_name_filter}%"))
    if last_name_filter:
        query = query.filter(Subscriber.last_name.ilike(f"%{last_name_filter}%"))
    if title_filter:
        query = query.filter(Subscriber.title.ilike(f"%{title_filter}%"))

    # Sortering
    if sort_order == "first_name":
        query = query.order_by(Subscriber.first_name.asc())
    elif sort_order == "last_name":
        query = query.order_by(Subscriber.last_name.asc())
    elif sort_order == "title":
        query = query.order_by(Subscriber.title.asc())
    elif sort_order == "oldest":
        query = query.order_by(Subscriber.created_at.asc())
    else:  # newest
        query = query.order_by(Subscriber.created_at.desc())

    subs = query.all()
    return render_template(
        "admin.html",
        subs=subs,
        first_name_filter=first_name_filter,
        last_name_filter=last_name_filter,
        title_filter=title_filter,
        sort_order=sort_order
    )

# --- 4. NY FUNKTION: TA BORT PRENUMERANT ---
@bp.route("/delete", methods=["POST"])
def delete_subscriber():
    from app.data.storage import subscribers
    
    if not session.get("is_admin"):
        return redirect(url_for("admin_bp.login"))
        
    email_to_delete = request.form.get("email")
    
    # Vi loopar igenom listan och tar bort den som matchar email
    # (global säger att vi vill ändra den globala variabeln subscribers)
    initial_count = len(subscribers)
    subscribers[:] = [p for p in subscribers if p.get('email') != email_to_delete]
    
    if len(subscribers) < initial_count:
        flash(f"Tog bort prenumerant: {email_to_delete}", "success")
    else:
        flash("Kunde inte hitta prenumeranten.", "error")
        
    return redirect(url_for("admin_bp.admin_dashboard"))


# --- 5. SUBSCRIBERS LIST (Using Service/Repository Pattern) ---
@bp.route("/subscribers", methods=["GET"])
@login_required
def subscribers_list():
    """
    Display all subscribers using the three-layer architecture.
    Route → Service → Repository → Model
    """
    from app.business.services import SubscriptionService
    from app.app import db
    
    try:
        service = SubscriptionService(db)
        subscribers_data = service.get_all_subscribers()
        count = service.get_subscriber_count()
        return render_template("subscribers.html", 
                             subscribers=subscribers_data, 
                             count=count)
    except Exception as e:
        flash(f"Ett fel inträffade: {str(e)}", "error")
        return render_template("subscribers.html", 
                             subscribers=[], 
                             count=0)


# --- 6. CSV EXPORT ---
@bp.route("/export/csv", methods=["GET"])
@login_required
def export_csv():
    """Export all subscribers to CSV format."""
    import io
    import csv
    from datetime import datetime
    from flask import Response
    from app.business.services import SubscriptionService
    from app.app import db
    
    try:
        service = SubscriptionService(db)
        subscribers_data = service.get_all_subscribers()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Company', 'Title', 'Created At'])
        
        # Write data rows
        for sub in subscribers_data:
            writer.writerow([
                sub.id,
                sub.first_name,
                sub.last_name,
                sub.email,
                sub.company,
                sub.title,
                sub.created_at.strftime('%Y-%m-%d %H:%M:%S') if sub.created_at else ''
            ])
        # Create response
        output.seek(0)
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        filename = f'subscribers-{timestamp}.csv'
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
    except Exception as e:
        flash(f"Error exporting CSV: {str(e)}", "error")
        return redirect(url_for("admin_bp.subscribers_list"))