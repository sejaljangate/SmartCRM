from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models import Followup, Customer, Lead, User, Activity

followups_bp = Blueprint("followups", __name__, url_prefix="/followups")

PER_PAGE = 10
FOLLOWUP_STATUSES = ["Scheduled", "Completed", "Cancelled"]  # "Overdue" is computed, not stored


def compute_display_status(followup):
    """
    A Scheduled follow-up whose date has already passed is shown as
    'Overdue' in the UI, without changing what's stored in the database.
    """
    if followup.status == "Scheduled" and followup.followup_date < date.today():
        return "Overdue"
    return followup.status


@followups_bp.route("/")
@login_required
def list_followups():
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = Followup.query

    if status_filter == "Overdue":
        query = query.filter(
            Followup.status == "Scheduled",
            Followup.followup_date < date.today(),
        )
    elif status_filter in FOLLOWUP_STATUSES:
        query = query.filter(Followup.status == status_filter)

    query = query.order_by(Followup.followup_date.asc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "followups/list.html",
        followups=pagination.items,
        pagination=pagination,
        status_filter=status_filter,
        compute_display_status=compute_display_status,
    )


@followups_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_followup():
    customers = Customer.query.order_by(Customer.full_name).all()
    leads = Lead.query.order_by(Lead.lead_name).all()
    employees = User.query.filter_by(is_active_user=True).all()

    if request.method == "POST":
        followup_date = request.form.get("followup_date", "")

        if not followup_date:
            flash("Follow-up date is required.", "danger")
            return render_template(
                "followups/form.html", followup=None, form_data=request.form,
                customers=customers, leads=leads, employees=employees,
            )

        followup = Followup(
            customer_id=request.form.get("customer_id") or None,
            lead_id=request.form.get("lead_id") or None,
            assigned_to=request.form.get("assigned_to") or None,
            followup_date=followup_date,
            followup_time=request.form.get("followup_time") or None,
            purpose=request.form.get("purpose", "").strip(),
            notes=request.form.get("notes", "").strip(),
            status="Scheduled",
        )
        db.session.add(followup)
        db.session.flush()

        if followup.customer_id:
            db.session.add(Activity(
                customer_id=followup.customer_id,
                description=f"Follow-up scheduled for {followup.followup_date}."
            ))

        db.session.commit()
        flash("Follow-up scheduled successfully.", "success")
        return redirect(url_for("followups.list_followups"))

    return render_template(
        "followups/form.html", followup=None, form_data=None,
        customers=customers, leads=leads, employees=employees,
    )


@followups_bp.route("/<int:followup_id>/edit", methods=["GET", "POST"])
@login_required
def edit_followup(followup_id):
    followup = Followup.query.get_or_404(followup_id)
    customers = Customer.query.order_by(Customer.full_name).all()
    leads = Lead.query.order_by(Lead.lead_name).all()
    employees = User.query.filter_by(is_active_user=True).all()

    if request.method == "POST":
        followup_date = request.form.get("followup_date", "")

        if not followup_date:
            flash("Follow-up date is required.", "danger")
            return render_template(
                "followups/form.html", followup=followup, form_data=request.form,
                customers=customers, leads=leads, employees=employees,
            )

        followup.customer_id = request.form.get("customer_id") or None
        followup.lead_id = request.form.get("lead_id") or None
        followup.assigned_to = request.form.get("assigned_to") or None
        followup.followup_date = followup_date
        followup.followup_time = request.form.get("followup_time") or None
        followup.purpose = request.form.get("purpose", "").strip()
        followup.notes = request.form.get("notes", "").strip()

        db.session.commit()
        flash("Follow-up updated successfully.", "success")
        return redirect(url_for("followups.list_followups"))

    return render_template(
        "followups/form.html", followup=followup, form_data=None,
        customers=customers, leads=leads, employees=employees,
    )


@followups_bp.route("/<int:followup_id>/complete", methods=["POST"])
@login_required
def complete_followup(followup_id):
    followup = Followup.query.get_or_404(followup_id)
    followup.status = "Completed"

    if followup.customer_id:
        db.session.add(Activity(
            customer_id=followup.customer_id,
            description="Follow-up marked as completed."
        ))

    db.session.commit()
    flash("Follow-up marked as completed.", "success")
    return redirect(url_for("followups.list_followups"))


@followups_bp.route("/<int:followup_id>/cancel", methods=["POST"])
@login_required
def cancel_followup(followup_id):
    followup = Followup.query.get_or_404(followup_id)
    followup.status = "Cancelled"
    db.session.commit()
    flash("Follow-up cancelled.", "info")
    return redirect(url_for("followups.list_followups"))


@followups_bp.route("/<int:followup_id>/delete", methods=["POST"])
@login_required
def delete_followup(followup_id):
    followup = Followup.query.get_or_404(followup_id)
    db.session.delete(followup)
    db.session.commit()
    flash("Follow-up deleted successfully.", "success")
    return redirect(url_for("followups.list_followups"))