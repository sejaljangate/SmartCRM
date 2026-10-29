from datetime import date, datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from extensions import db
from models import Customer, Lead, Followup, Deal, Activity

dashboard_bp = Blueprint("dashboard", __name__)


def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


@dashboard_bp.route("/dashboard")
@login_required
def index():
    # --- Top stat cards ---
    total_customers = Customer.query.count()
    total_leads = Lead.query.count()

    pending_followups = Followup.query.filter(
        Followup.status == "Scheduled"
    ).count()

    overdue_count = Followup.query.filter(
        Followup.status == "Scheduled",
        Followup.followup_date < date.today(),
    ).count()

    total_revenue = db.session.query(
        func.coalesce(func.sum(Deal.deal_amount), 0)
    ).filter(Deal.status == "Won").scalar()

    open_deals = Deal.query.filter(Deal.status == "Negotiation").count()

    # --- Sales Overview chart: revenue of Won deals, grouped by month ---
    sales_rows = (
        db.session.query(
            func.date_format(Deal.deal_date, "%Y-%m").label("month"),
            func.sum(Deal.deal_amount).label("total"),
        )
        .filter(Deal.status == "Won")
        .group_by("month")
        .order_by("month")
        .all()
    )
    sales_labels = [row.month for row in sales_rows]
    sales_totals = [float(row.total) for row in sales_rows]

    # --- Lead Status chart: count of leads per status ---
    status_rows = (
        db.session.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )
    lead_status_labels = [row[0] for row in status_rows]
    lead_status_counts = [row[1] for row in status_rows]

    # --- Recent customers (last 5 added) ---
    recent_customers = (
        Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
    )

    # --- Upcoming follow-ups (scheduled, today or later) ---
    upcoming_followups = (
        Followup.query.filter(
            Followup.status == "Scheduled",
            Followup.followup_date >= date.today(),
        )
        .order_by(Followup.followup_date.asc())
        .limit(5)
        .all()
    )

    # --- Overdue follow-ups (scheduled, date already passed) ---
    overdue_followups = (
        Followup.query.filter(
            Followup.status == "Scheduled",
            Followup.followup_date < date.today(),
        )
        .order_by(Followup.followup_date.asc())
        .all()
    )

    # --- Recent activity feed (global, across all customers) ---
    recent_activity = (
        Activity.query.order_by(Activity.created_at.desc()).limit(8).all()
    )

    return render_template(
        "dashboard.html",
        greeting=get_greeting(),
        total_customers=total_customers,
        total_leads=total_leads,
        pending_followups=pending_followups,
        overdue_count=overdue_count,
        total_revenue=total_revenue,
        open_deals=open_deals,
        sales_labels=sales_labels,
        sales_totals=sales_totals,
        lead_status_labels=lead_status_labels,
        lead_status_counts=lead_status_counts,
        recent_customers=recent_customers,
        upcoming_followups=upcoming_followups,
        overdue_followups=overdue_followups,
        recent_activity=recent_activity,
        today=date.today(),
    )