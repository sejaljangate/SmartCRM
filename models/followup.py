from datetime import datetime
from extensions import db


class Followup(db.Model):
    __tablename__ = "followups"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    followup_date = db.Column(db.Date, nullable=False)
    followup_time = db.Column(db.Time, nullable=True)

    purpose = db.Column(db.String(200))
    notes = db.Column(db.Text)

    # Scheduled, Completed, Cancelled  (Overdue is calculated, not stored)
    status = db.Column(db.String(20), default="Scheduled")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Followup {self.followup_date} ({self.status})>"