import datetime
import json
from flask import jsonify
from app import db


# Створюємо модель товару
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    pictures = db.Column(db.JSON, default=[], nullable=False)
    price = db.Column(db.Float, nullable=False, default=0)
    discount = db.Column(db.Float, nullable=False, default=0)
    stock = db.Column(db.Integer, default=1, nullable=False)
    specs = db.Column(db.JSON, default={}, nullable=False)
    desc = db.Column(db.Text, nullable=True)
    updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, title, pictures=None, price=None, discount=None, stock=None, specs=None, desc=None):
        self.title = title
        self.pictures = pictures
        self.price = price
        self.discount = discount
        self.stock = stock
        if specs != '':
            self.specs = json.loads(specs)
        else:
            self.specs = {}
        self.desc = desc

    def in_stock(self):
        return self.stock > 0

    def bought(self, number: int):
        if number > self.stock or number <= 0:
            raise ValueError
        self.stock -= number
        return number * (self.price - self.discount)

    def acquired(self, number: int):
        if number <= 0:
            raise ValueError
        self.stock += number

    def in_specs(self, text: str):
        for spec in self.specs:
            if text in spec or text in self.specs[spec]:
                return True
        return False

    def as_json_response(self):
        return jsonify(self.as_dict())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def products_as_json_response(products: list):
        return jsonify([*map(Product.as_dict, products)])
