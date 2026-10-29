from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import User
from utils.decorators import admin_required

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/")
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("users/list.html", users=users)


@users_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "employee")

        if not full_name or not email or not password:
            flash("Full name, email and password are required.", "danger")
            return render_template("users/form.html", user=None, form_data=request.form)

        if role not in ("admin", "employee"):
            role = "employee"

        if User.query.filter_by(email=email).first():
            flash("A user with this email already exists.", "danger")
            return render_template("users/form.html", user=None, form_data=request.form)

        new_user = User(full_name=full_name, email=email, phone=phone, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Employee added successfully.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", user=None, form_data=None)


@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not full_name or not email:
            flash("Full name and email are required.", "danger")
            return render_template("users/form.html", user=user, form_data=request.form)

        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            flash("Another user already uses this email.", "danger")
            return render_template("users/form.html", user=user, form_data=request.form)

        user.full_name = full_name
        user.email = email
        user.phone = request.form.get("phone", "").strip()
        user.role = request.form.get("role", user.role)

        new_password = request.form.get("password", "")
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", user=user, form_data=None)


@users_bp.route("/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("users.list_users"))

    user.is_active_user = not user.is_active_user
    db.session.commit()

    status_text = "activated" if user.is_active_user else "deactivated"
    flash(f"{user.full_name} has been {status_text}.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("users.list_users"))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for("users.list_users"))