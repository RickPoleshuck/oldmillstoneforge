from datetime import datetime

from extensions import db
from time_utils import format_minutes


class Slot(db.Model):
    """A bookable meeting time, created by the admin, with a capacity limit."""

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=180)
    capacity = db.Column(db.Integer, nullable=False, default=5)
    label = db.Column(db.String(255))  # optional, e.g. "1:1 with Jordan"
    created_at = db.Column(db.DateTime, default=datetime.now)
    signups = db.relationship("Signup", backref="slot", cascade="all, delete-orphan")

    @property
    def booked_count(self):
        return len(self.signups)

    @property
    def spots_left(self):
        return max(self.capacity - self.booked_count, 0)

    @property
    def is_full(self):
        return self.spots_left <= 0

    def duration(self):
        return format_minutes(self.duration_minutes)
