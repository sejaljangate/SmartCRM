from datetime import datetime
from extensions import db


class Activity(db.Model):
    """
    A simple activity log used to build the Customer 360 timeline
    (e.g. 'Lead created', 'Follow-up completed', 'Deal marked Won').
    """
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Activity {self.description}>"