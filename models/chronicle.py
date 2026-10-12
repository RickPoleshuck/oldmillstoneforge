from datetime import datetime

from extensions import db


class Chronicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    filename = db.Column(db.String, nullable=False)
    pdf = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
