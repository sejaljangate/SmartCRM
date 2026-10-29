
from app import app
from extensions import db
from models import User

with app.app_context():
    user = User.query.filter_by(
        email="sejaljangate@gmail.com"
    ).first()

    if user:
        user.set_password("Admin@12345")
        db.session.commit()
        print("Password reset done")
    else:
        print("Admin user not found")