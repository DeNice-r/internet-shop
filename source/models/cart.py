import datetime
from flask import jsonify
from flask_login import current_user
from app import db
from models.user import User


class Cart(db.Model):
    session_id = db.Column(db.String(128), primary_key=True, nullable=False)
    customer = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    items = db.Column(db.JSON, default={})
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, session_id: str, items=None):
        self.session_id = session_id
        if items is not None:
            self.items = items
        self.customer = current_user.id

    def as_json_response(self):
        return jsonify(self.as_dict())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}