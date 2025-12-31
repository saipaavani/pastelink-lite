from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Paste(db.Model):
    __tablename__ = "pastes"

    id = db.Column(db.String, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    max_views = db.Column(db.Integer, nullable=True)
    view_count = db.Column(db.Integer, default=0)