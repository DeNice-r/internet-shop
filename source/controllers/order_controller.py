from flask import render_template, Blueprint, flash, redirect, url_for
from itsdangerous import URLSafeTimedSerializer
from app import app
from models.order import Order


order = Blueprint('order', __name__)


def confirm_token(token, expiration=31536000):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email


@order.route("/order/<order_token>")
def get_order(order_token):
    try:
        order_id = confirm_token(order_token)
    except:
        flash('Замовлення не знайдено.', 'danger')
        return redirect(url_for('products.index'))
    order_ = Order.query.get(order_id)
    return render_template("order/order_info.html", order=order_, order_token=order_token)