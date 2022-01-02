import datetime
from app import db
from models.user import User
from flask_login import current_user


# Створюємо модель новини
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(16), nullable=True)
    author = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, title, content, picture):
        self.title = title
        self.content = content
        self.picture = picture
        self.author = current_user.id if current_user.is_authenticated else None

    def get_author_name(self):
        return User.query.get(self.author).username
