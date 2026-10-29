from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models import Customer, Lead, Followup, Deal, Activity

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

PER_PAGE = 10


@customers_bp.route("/")
@login_required
def list_customers():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "")
    sort = request.args.get("sort", "created_at_desc")
    page = request.args.get("page", 1, type=int)

    query = Customer.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Customer.full_name.ilike(like),
                Customer.company_name.ilike(like),
                Customer.email.ilike(like),
            )
        )

    if status_filter in ("Active", "Inactive"):
        query = query.filter(Customer.status == status_filter)

    sort_map = {
        "name_asc": Customer.full_name.asc(),
        "name_desc": Customer.full_name.desc(),
        "created_at_desc": Customer.created_at.desc(),
        "created_at_asc": Customer.created_at.asc(),
    }
    query = query.order_by(sort_map.get(sort, Customer.created_at.desc()))

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "customers/list.html",
        customers=pagination.items,
        pagination=pagination,
        search=search,
        status_filter=status_filter,
        sort=sort,
    )


@customers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_customer():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()

        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("customers/form.html", customer=None, form_data=request.form)

        customer = Customer(
            full_name=full_name,
            company_name=request.form.get("company_name", "").strip(),
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip(),
            address=request.form.get("address", "").strip(),
            customer_type=request.form.get("customer_type", "").strip(),
            status=request.form.get("status", "Active"),
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(customer)
        db.session.flush()  # gets customer.id before commit

        db.session.add(Activity(
            customer_id=customer.id,
            description="Customer created."
        ))
        db.session.commit()

        flash("Customer added successfully.", "success")
        return redirect(url_for("customers.list_customers"))

    return render_template("customers/form.html", customer=None, form_data=None)


@customers_bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()

        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("customers/form.html", customer=customer, form_data=request.form)

        customer.full_name = full_name
        customer.company_name = request.form.get("company_name", "").strip()
        customer.email = request.form.get("email", "").strip()
        customer.phone = request.form.get("phone", "").strip()
        customer.address = request.form.get("address", "").strip()
        customer.customer_type = request.form.get("customer_type", "").strip()
        customer.status = request.form.get("status", "Active")
        customer.notes = request.form.get("notes", "").strip()

        db.session.add(Activity(
            customer_id=customer.id,
            description="Customer details updated."
        ))
        db.session.commit()

        flash("Customer updated successfully.", "success")
        return redirect(url_for("customers.list_customers"))

    return render_template("customers/form.html", customer=customer, form_data=None)


@customers_bp.route("/<int:customer_id>")
@login_required
def view_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    leads = Lead.query.filter_by(customer_id=customer.id).order_by(Lead.created_at.desc()).all()
    followups = Followup.query.filter_by(customer_id=customer.id).order_by(Followup.followup_date.desc()).all()
    deals = Deal.query.filter_by(customer_id=customer.id).order_by(Deal.deal_date.desc()).all()
    activities = Activity.query.filter_by(customer_id=customer.id).order_by(Activity.created_at.desc()).all()

    total_deal_value = sum(float(d.deal_amount) for d in deals if d.status == "Won")

    return render_template(
        "customers/view.html",
        customer=customer,
        leads=leads,
        followups=followups,
        deals=deals,
        activities=activities,
        total_deal_value=total_deal_value,
    )


@customers_bp.route("/<int:customer_id>/delete", methods=["POST"])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted successfully.", "success")
    return redirect(url_for("customers.list_customers"))