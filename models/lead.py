from datetime import datetime
from extensions import db


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)

    lead_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(120))

    # Website, Referral, Social Media, Advertisement, Direct Enquiry, Other
    lead_source = db.Column(db.String(50))

    expected_value = db.Column(db.Numeric(12, 2), default=0)

    # New, Contacted, Interested, Negotiation, Won, Lost
    status = db.Column(db.String(20), default="New")

    notes = db.Column(db.Text)

    # A lead may already be linked to an existing customer (optional).
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)

    # Which employee this lead is assigned to.
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    followups = db.relationship("Followup", backref="lead", lazy=True)

    def __repr__(self):
        return f"<Lead {self.lead_name} ({self.status})>"