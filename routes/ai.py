from flask import Blueprint, jsonify
from flask_login import login_required

from models import Customer
from utils.ai_helper import draft_followup_email, summarize_customer

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.route("/customers/<int:customer_id>/email", methods=["POST"])
@login_required
def draft_email(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    text, error = draft_followup_email(customer)
    if error:
        return jsonify(ok=False, error=error), 503
    return jsonify(ok=True, text=text)


@ai_bp.route("/customers/<int:customer_id>/summary", methods=["POST"])
@login_required
def summarize(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    text, error = summarize_customer(customer)
    if error:
        return jsonify(ok=False, error=error), 503
    return jsonify(ok=True, text=text)