from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models import Lead, Customer, User, Activity

leads_bp = Blueprint("leads", __name__, url_prefix="/leads")

PER_PAGE = 10

LEAD_SOURCES = ["Website", "Referral", "Social Media", "Advertisement", "Direct Enquiry", "Other"]
LEAD_STATUSES = ["New", "Contacted", "Interested", "Negotiation", "Won", "Lost"]


@leads_bp.route("/")
@login_required
def list_leads():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = Lead.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Lead.lead_name.ilike(like),
                Lead.company.ilike(like),
                Lead.email.ilike(like),
            )
        )

    if status_filter in LEAD_STATUSES:
        query = query.filter(Lead.status == status_filter)

    query = query.order_by(Lead.created_at.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "leads/list.html",
        leads=pagination.items,
        pagination=pagination,
        search=search,
        status_filter=status_filter,
        statuses=LEAD_STATUSES,
    )


@leads_bp.route("/kanban")
@login_required
def kanban_leads():
    columns = {status: [] for status in LEAD_STATUSES}
    all_leads = Lead.query.order_by(Lead.created_at.desc()).all()

    for lead in all_leads:
        if lead.status in columns:
            columns[lead.status].append(lead)

    return render_template("leads/kanban.html", columns=columns, statuses=LEAD_STATUSES)


@leads_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_lead():
    employees = User.query.filter_by(is_active_user=True).all()
    customers = Customer.query.order_by(Customer.full_name).all()

    if request.method == "POST":
        lead_name = request.form.get("lead_name", "").strip()

        if not lead_name:
            flash("Lead name is required.", "danger")
            return render_template(
                "leads/form.html", lead=None, form_data=request.form,
                employees=employees, customers=customers,
                sources=LEAD_SOURCES, statuses=LEAD_STATUSES,
            )

        expected_value = request.form.get("expected_value") or 0
        customer_id = request.form.get("customer_id") or None
        assigned_to = request.form.get("assigned_to") or None

        lead = Lead(
            lead_name=lead_name,
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip(),
            company=request.form.get("company", "").strip(),
            lead_source=request.form.get("lead_source", "").strip(),
            expected_value=expected_value,
            status=request.form.get("status", "New"),
            notes=request.form.get("notes", "").strip(),
            customer_id=customer_id,
            assigned_to=assigned_to,
        )
        db.session.add(lead)
        db.session.flush()

        if lead.customer_id:
            db.session.add(Activity(
                customer_id=lead.customer_id,
                description=f"Lead '{lead.lead_name}' created."
            ))

        db.session.commit()
        flash("Lead added successfully.", "success")
        return redirect(url_for("leads.list_leads"))

    return render_template(
        "leads/form.html", lead=None, form_data=None,
        employees=employees, customers=customers,
        sources=LEAD_SOURCES, statuses=LEAD_STATUSES,
    )


@leads_bp.route("/<int:lead_id>/edit", methods=["GET", "POST"])
@login_required
def edit_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    employees = User.query.filter_by(is_active_user=True).all()
    customers = Customer.query.order_by(Customer.full_name).all()

    if request.method == "POST":
        lead_name = request.form.get("lead_name", "").strip()

        if not lead_name:
            flash("Lead name is required.", "danger")
            return render_template(
                "leads/form.html", lead=lead, form_data=request.form,
                employees=employees, customers=customers,
                sources=LEAD_SOURCES, statuses=LEAD_STATUSES,
            )

        old_status = lead.status

        lead.lead_name = lead_name
        lead.email = request.form.get("email", "").strip()
        lead.phone = request.form.get("phone", "").strip()
        lead.company = request.form.get("company", "").strip()
        lead.lead_source = request.form.get("lead_source", "").strip()
        lead.expected_value = request.form.get("expected_value") or 0
        lead.status = request.form.get("status", "New")
        lead.notes = request.form.get("notes", "").strip()
        lead.customer_id = request.form.get("customer_id") or None
        lead.assigned_to = request.form.get("assigned_to") or None

        if lead.customer_id and old_status != lead.status:
            db.session.add(Activity(
                customer_id=lead.customer_id,
                description=f"Lead '{lead.lead_name}' status changed from {old_status} to {lead.status}."
            ))

        db.session.commit()
        flash("Lead updated successfully.", "success")
        return redirect(url_for("leads.list_leads"))

    return render_template(
        "leads/form.html", lead=lead, form_data=None,
        employees=employees, customers=customers,
        sources=LEAD_SOURCES, statuses=LEAD_STATUSES,
    )


@leads_bp.route("/<int:lead_id>/delete", methods=["POST"])
@login_required
def delete_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    flash("Lead deleted successfully.", "success")
    return redirect(url_for("leads.list_leads"))