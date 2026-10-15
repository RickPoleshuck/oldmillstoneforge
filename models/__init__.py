"""
Models package.

Re-exports every model class so the rest of the app can simply do:

    from models import User, Slot, Signup

Importing them here also guarantees each model is registered with
SQLAlchemy's metadata before `db.create_all()` is called.
"""
from models.chronicle import Chronicle
from models.picture import Picture
from models.user import User
from models.slot import Slot
from models.signup import Signup

__all__ = ["User", "Slot", "Signup", 'Picture', 'Chronicle']
