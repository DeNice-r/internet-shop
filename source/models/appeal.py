import datetime
from app import db
from models.user import User
from flask_login import current_user


# Створюємо модель новини
class Appeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    customer = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    phone = db.Column(db.String(13), nullable=True)
    email = db.Column(db.String(320), nullable=True)
    firstname = db.Column(db.String(50), default='Клієнт', nullable=True)
    support_comment = db.Column(db.Text, nullable=True)
    closed = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, title, content, firstname, phone, email):
        self.title = title
        self.content = content
        self.firstname = firstname
        self.phone = phone
        self.email = email
        self.customer = current_user.id
        print(current_user.id)
