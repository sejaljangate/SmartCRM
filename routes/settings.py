from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")

        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("settings.html")

        current_user.full_name = full_name
        current_user.phone = phone

        if new_password:
            if not current_user.check_password(current_password):
                flash("Current password is incorrect. Password was not changed.", "danger")
                return render_template("settings.html")
            current_user.set_password(new_password)
            flash("Profile and password updated successfully.", "success")
        else:
            flash("Profile updated successfully.", "success")

        db.session.commit()
        return redirect(url_for("settings.index"))

    return render_template("settings.html")