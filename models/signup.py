from datetime import datetime

from extensions import db


class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slot.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint("user_id", "slot_id", name="uq_user_slot"),)
