import csv
import io

from flask import Blueprint, render_template, Response
from flask_login import login_required
from sqlalchemy import func

from extensions import db
from models import Deal, Lead, User

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def get_report_data():
    """
    Shared query logic used by both the reports page and the CSV export,
    so the numbers you see on screen always match what you download.
    """
    # --- Sales Analytics ---
    revenue_rows = (
        db.session.query(
            func.date_format(Deal.deal_date, "%Y-%m").label("month"),
            func.sum(Deal.deal_amount).label("total"),
        )
        .filter(Deal.status == "Won")
        .group_by("month")
        .order_by("month")
        .all()
    )
    revenue_labels = [r.month for r in revenue_rows]
    revenue_totals = [float(r.total) for r in revenue_rows]

    won_deals = Deal.query.filter_by(status="Won").count()
    lost_deals = Deal.query.filter_by(status="Lost").count()
    negotiation_deals = Deal.query.filter_by(status="Negotiation").count()
    total_deal_count = Deal.query.count()

    # --- Lead Analytics ---
    total_leads = Lead.query.count()
    converted_leads = Lead.query.filter_by(status="Won").count()
    lost_leads = Lead.query.filter_by(status="Lost").count()
    conversion_rate = (converted_leads / total_leads * 100) if total_leads else 0

    # --- Employee Performance: won deals + revenue per employee ---
    employee_rows = (
        db.session.query(
            User.full_name,
            func.count(Deal.id).label("deals_won"),
            func.coalesce(func.sum(Deal.deal_amount), 0).label("revenue"),
        )
        .join(Deal, Deal.assigned_to == User.id)
        .filter(Deal.status == "Won")
        .group_by(User.id, User.full_name)
        .order_by(func.sum(Deal.deal_amount).desc())
        .all()
    )

    return {
        "revenue_labels": revenue_labels,
        "revenue_totals": revenue_totals,
        "won_deals": won_deals,
        "lost_deals": lost_deals,
        "negotiation_deals": negotiation_deals,
        "total_deal_count": total_deal_count,
        "total_leads": total_leads,
        "converted_leads": converted_leads,
        "lost_leads": lost_leads,
        "conversion_rate": conversion_rate,
        "employee_rows": employee_rows,
    }


@reports_bp.route("/")
@login_required
def index():
    data = get_report_data()
    return render_template("reports/index.html", **data)


@reports_bp.route("/export/deals.csv")
@login_required
def export_deals_csv():
    deals = Deal.query.order_by(Deal.deal_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Deal Name", "Customer", "Amount", "Date", "Status", "Assigned Employee"])

    for d in deals:
        writer.writerow([
            d.deal_name,
            d.customer.full_name if d.customer else "",
            float(d.deal_amount),
            d.deal_date,
            d.status,
            d.assigned_employee.full_name if d.assigned_employee else "",
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=deals_export.csv"},
    )