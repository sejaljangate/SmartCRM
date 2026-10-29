from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func

from extensions import db
from models import Deal, Customer, User, Activity

deals_bp = Blueprint("deals", __name__, url_prefix="/deals")

PER_PAGE = 10
DEAL_STATUSES = ["Negotiation", "Won", "Lost"]


@deals_bp.route("/")
@login_required
def list_deals():
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = Deal.query

    if status_filter in DEAL_STATUSES:
        query = query.filter(Deal.status == status_filter)

    query = query.order_by(Deal.deal_date.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    # --- Dynamic summary panel (based on ALL deals, not just this page) ---
    total_revenue = db.session.query(
        func.coalesce(func.sum(Deal.deal_amount), 0)
    ).filter(Deal.status == "Won").scalar()

    won_count = Deal.query.filter_by(status="Won").count()
    lost_count = Deal.query.filter_by(status="Lost").count()

    avg_deal_value = db.session.query(
        func.coalesce(func.avg(Deal.deal_amount), 0)
    ).filter(Deal.status == "Won").scalar()

    return render_template(
        "deals/list.html",
        deals=pagination.items,
        pagination=pagination,
        status_filter=status_filter,
        total_revenue=total_revenue,
        won_count=won_count,
        lost_count=lost_count,
        avg_deal_value=avg_deal_value,
    )


@deals_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_deal():
    customers = Customer.query.order_by(Customer.full_name).all()
    employees = User.query.filter_by(is_active_user=True).all()

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        deal_name = request.form.get("deal_name", "").strip()
        deal_date = request.form.get("deal_date", "")

        if not customer_id or not deal_name or not deal_date:
            flash("Customer, deal name, and deal date are required.", "danger")
            return render_template(
                "deals/form.html", deal=None, form_data=request.form,
                customers=customers, employees=employees, statuses=DEAL_STATUSES,
            )

        deal = Deal(
            customer_id=customer_id,
            assigned_to=request.form.get("assigned_to") or None,
            deal_name=deal_name,
            deal_amount=request.form.get("deal_amount") or 0,
            deal_date=deal_date,
            status=request.form.get("status", "Negotiation"),
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(deal)
        db.session.flush()

        db.session.add(Activity(
            customer_id=deal.customer_id,
            description=f"Deal '{deal.deal_name}' created."
        ))
        db.session.commit()

        flash("Deal added successfully.", "success")
        return redirect(url_for("deals.list_deals"))

    return render_template(
        "deals/form.html", deal=None, form_data=None,
        customers=customers, employees=employees, statuses=DEAL_STATUSES,
    )


@deals_bp.route("/<int:deal_id>/edit", methods=["GET", "POST"])
@login_required
def edit_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    customers = Customer.query.order_by(Customer.full_name).all()
    employees = User.query.filter_by(is_active_user=True).all()

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        deal_name = request.form.get("deal_name", "").strip()
        deal_date = request.form.get("deal_date", "")

        if not customer_id or not deal_name or not deal_date:
            flash("Customer, deal name, and deal date are required.", "danger")
            return render_template(
                "deals/form.html", deal=deal, form_data=request.form,
                customers=customers, employees=employees, statuses=DEAL_STATUSES,
            )

        old_status = deal.status

        deal.customer_id = customer_id
        deal.assigned_to = request.form.get("assigned_to") or None
        deal.deal_name = deal_name
        deal.deal_amount = request.form.get("deal_amount") or 0
        deal.deal_date = deal_date
        deal.status = request.form.get("status", "Negotiation")
        deal.notes = request.form.get("notes", "").strip()

        if old_status != deal.status:
            db.session.add(Activity(
                customer_id=deal.customer_id,
                description=f"Deal '{deal.deal_name}' status changed from {old_status} to {deal.status}."
            ))

        db.session.commit()
        flash("Deal updated successfully.", "success")
        return redirect(url_for("deals.list_deals"))

    return render_template(
        "deals/form.html", deal=deal, form_data=None,
        customers=customers, employees=employees, statuses=DEAL_STATUSES,
    )


@deals_bp.route("/<int:deal_id>/delete", methods=["POST"])
@login_required
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    db.session.delete(deal)
    db.session.commit()
    flash("Deal deleted successfully.", "success")
    return redirect(url_for("deals.list_deals"))