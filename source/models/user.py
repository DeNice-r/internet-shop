import datetime
from app import db, lm
from flask_login import UserMixin
import json


# Створюємо модель користувача
class User(db.Model, UserMixin):
    ROLES = {'admin': 'editor', 'editor': ''}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(13), nullable=True)
    firstname = db.Column(db.String(50), nullable=True)
    settlement = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    roles = db.Column(db.JSON, nullable=False, default='[""]')
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    last_login = db.Column(db.DateTime, nullable=True, default=None)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, email, password, phone=None, firstname=None, settlement=None, address=None):
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.firstname = firstname
        self.settlement = settlement
        self.address = address

    def has_role(self, role: str) -> bool:
        roles = json.loads(self.roles)
        return role in roles

    def add_role(self, role):
        roles = json.loads(self.roles)
        if role not in roles:
            roles.append(role)
        while roles[-1] in User.ROLES and User.ROLES[roles[-1]] not in roles:
            roles.append(User.ROLES[roles[-1]])
        self.roles = json.dumps(list(set(roles)))


# Надаємо можливість завантажувати користувача менеджеру авторизації
@lm.user_loader
def user_loader(user_id):
    return User.query.get(user_id)
