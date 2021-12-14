import datetime
from app import db
from models.user import User


# Створюємо модель новини
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    comment = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.String(13), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    settlement = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    products = db.Column(db.JSON, nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, title, content, picture, author):
        self.title = title
        self.content = content
        self.picture = picture
        self.author = author
