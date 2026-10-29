from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import text

from config import Config
from extensions import db, login_manager


def create_app():
    Config.validate()

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    with app.app_context():
        from models import User, Customer, Lead, Followup, Deal, Activity
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_notifications():
        from datetime import date
        from models import Followup

        if not current_user.is_authenticated:
            return dict(nav_overdue_followups=[], nav_today_followups=[])

        today = date.today()

        overdue = (
            Followup.query.filter(
                Followup.status == "Scheduled",
                Followup.followup_date < today,
            )
            .order_by(Followup.followup_date.asc())
            .limit(5)
            .all()
        )

        today_followups = (
            Followup.query.filter(
                Followup.status == "Scheduled",
                Followup.followup_date == today,
            )
            .order_by(Followup.followup_time.asc())
            .limit(5)
            .all()
        )

        return dict(nav_overdue_followups=overdue, nav_today_followups=today_followups)

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from routes.customers import customers_bp
    app.register_blueprint(customers_bp)

    from routes.leads import leads_bp
    app.register_blueprint(leads_bp)

    from routes.followups import followups_bp
    app.register_blueprint(followups_bp)

    from routes.deals import deals_bp
    app.register_blueprint(deals_bp)

    from routes.reports import reports_bp
    app.register_blueprint(reports_bp)

    from routes.users import users_bp
    app.register_blueprint(users_bp)

    from routes.settings import settings_bp
    app.register_blueprint(settings_bp)

    
    from routes.ai import ai_bp
    app.register_blueprint(ai_bp)

    from dotenv import load_dotenv
    load_dotenv()


    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return render_template("landing.html")
    
    @app.route("/db-check")
    def db_check():
        try:
            db.session.execute(text("SELECT 1"))
            return "MySQL connection successful."
        except Exception as e:
            return f"MySQL connection FAILED.<br>Error: {e}", 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()  # undo any partial/broken database transaction
        return render_template("errors/500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.FLASK_DEBUG)