import datetime
from app import db, lm
from flask_login import UserMixin, AnonymousUserMixin
import json


# Створюємо модель користувача
class User(db.Model, UserMixin):
    ROLES = {'admin': ('editor', 'support', 'seller'), 'editor': ('user',), 'seller': ('user',), 'support': ('user',)}
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
        roles = self.roles
        return role in roles

    def has_any_role(self, *roles) -> bool:
        try:
            for r in iter(roles[0]):
                if r in self.roles:
                    return True
        finally:
            for role in roles:
                if role in self.roles:
                    return True
        return False

    def add_role(self, role):
        roles = list(self.roles)
        if role not in roles:
            roles.append(role)
        while roles[-1] in User.ROLES and any(User.ROLES[roles[-1]]) not in roles:
            roles.extend(User.ROLES[roles[-1]])
        self.roles = list(set(roles))
        db.session.commit()


# Надаємо можливість завантажувати користувача менеджеру авторизації
@lm.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


class AnonymousUser(AnonymousUserMixin):
    def has_role(self, role):
        return False

    def has_any_role(self, *roles):
        return False


lm.anonymous_user = AnonymousUser