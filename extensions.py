"""
Shared Flask extension instances.

Kept in their own module (rather than created inside app.py) so that the
model files can import `db` without causing a circular import with app.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
