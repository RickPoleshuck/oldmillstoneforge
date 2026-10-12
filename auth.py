"""
Auth helpers: Flask-Login's user loader callback and the admin_required
route decorator. Split out from app.py since these aren't classes but are
still auth-related plumbing that app.py depends on.
"""

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

from extensions import login_manager
from models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("signups"))
        return view(*args, **kwargs)

    return wrapped
