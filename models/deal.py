from datetime import datetime
from extensions import db


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    deal_name = db.Column(db.String(150), nullable=False)
    deal_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    deal_date = db.Column(db.Date, nullable=False)

    # Negotiation, Won, Lost
    status = db.Column(db.String(20), default="Negotiation")

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Deal {self.deal_name} ({self.status})>"