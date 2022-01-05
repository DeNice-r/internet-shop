import datetime
from app import db
from models.user import User
from models.product import Product


order_status = {
    -1: "Відхилено",
    0: "Очікує на розгляд",
    1: "Розглянуто, очікуйте дзвінок",
    2: "Комплектується",
    3: "Відправлено",
    4: "Завершено"
}


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
    final_price = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.Integer, nullable=False, default=0)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, comment, phone, firstname, settlement, address, products):
        self.comment = comment
        self.phone = phone
        self.firstname = firstname
        self.settlement = settlement
        self.address = address
        self.products = products
        self.final_price = 0

        # Зменшуємо кількість товарів у наявності
        if len(products) == 0:
            raise ValueError
        for p in products:
            self.final_price += Product.query.get(p).bought(products[p])
        self.final_price = round(self.final_price, 2)
        db.session.commit()

    def set_status(self, status: int):
        if self.status != -1 and status == -1:
            for p in self.products:
                Product.query.get(p).acquired(self.products[p])
        if self.status == -1 and status != -1:
            for p in self.products:
                Product.query.get(p).bought(self.products[p])
        self.status = status

    def get_status_string(self):
        return order_status[self.status]

    def get_status_color(self):
        first = hex(int(255 - (self.status) * 255 / len(order_status)))[2:]
        second = hex(int((self.status) * 255 / len(order_status)))[2:]
        return '#' + (first if len(first) == 2 else '00') + (second if len(second) == 2 else '00') + 'ff'
