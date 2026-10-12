import logging
import os
from flask import Flask
from config import Config
from extensions import db, login_manager
from models import User
from routes import register_routes

# Newsletter PDFs: drop the files in static/chronicles/ (or point `url` elsewhere).
CHRONICLES = [
    {"label": "May 2024", "file": "OMF_Chronicle_1.pdf"},
    {"label": "June 2025", "file": "OMF_Chronicle_2.pdf"},
    {"label": "January 2026", "file": "OMF_Chronicle_3.pdf"},
]

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.logger.setLevel(logging.getLevelName(app.config['LOG_LEVEL'].upper()))

    # ensure database transactions are completed during a restart
    @app.teardown_appcontext
    def shutdown_session(_=None):
        db.session.remove()

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Routes
    register_routes(app)

    return app


def bootstrap_db(app):
    db.create_all()

    admin_userid = os.environ.get("ADMIN_USER_ID", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "password")

    if not User.query.filter_by(userid=admin_userid).first():
        admin = User(userid=admin_userid, name="Administrator", is_admin=True, is_active=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Created admin account: %s',admin_userid)


if __name__ == "__main__":
    main_app = create_app()
    with main_app.app_context():
        bootstrap_db(main_app)
    main_app.logger.info("Starting app.run")
    main_app.run(debug=True)
