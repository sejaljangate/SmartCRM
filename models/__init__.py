"""
Central import point for all models, so the rest of the app can do:
    from models import User, Customer, Lead, Followup, Deal, Activity
"""

from models.user import User
from models.customer import Customer
from models.lead import Lead
from models.followup import Followup
from models.deal import Deal
from models.activity import Activity