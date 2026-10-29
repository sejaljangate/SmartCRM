from datetime import datetime
from extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))

    # e.g. 'Individual', 'Business'
    customer_type = db.Column(db.String(50))

    # 'Active' or 'Inactive'
    status = db.Column(db.String(20), default="Active")

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One customer can have many leads, followups, deals, activities.
    leads = db.relationship("Lead", backref="customer", lazy=True)
    followups = db.relationship("Followup", backref="customer", lazy=True)
    deals = db.relationship("Deal", backref="customer", lazy=True)
    activities = db.relationship("Activity", backref="customer", lazy=True)

    def __repr__(self):
        return f"<Customer {self.full_name}>"