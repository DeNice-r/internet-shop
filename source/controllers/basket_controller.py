from flask import render_template, Blueprint, request, make_response, flash, redirect, url_for
from flask_login import current_user
from models.product import Product
from models.order import Order
from forms import OrderForm
from itsdangerous import URLSafeTimedSerializer
import json
from app import app, db


basket = Blueprint('basket', __name__)


def generate_order_token(order_id):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(str(order_id), salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=31536000):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email


@basket.route("/basket", methods=('GET', 'POST'))
def index():
    basket_json = request.cookies.get('basket')
    if basket_json:
        basket_ = json.loads(basket_json)
    else:
        basket_ = {}
    products = []
    for p in basket_:
        products.append(Product.query.get(p))
        if products[-1].stock == 0:
            products.pop()
        elif basket_[p] > products[-1].stock:
            basket_[p] = products[-1].stock

    form = OrderForm()

    if form.validate_on_submit():
        response = None
        print(form.comment.raw_data)
        try:
            order_ = Order(
                request.form.get('comment'),
                form.phone.data,
                form.firstname.data,
                form.settlement.data,
                form.address.data,
                basket_
            )
            if current_user.is_authenticated:
                order_.customer = current_user.id
            db.session.add(order_)
            db.session.commit()
            response = make_response(redirect(url_for('basket.order', order_token=generate_order_token(order_.id))))
        except ValueError as e:
            flash('Виникла помилка. Будь-ласка спробуйте повторити замовлення.' + str(e), 'danger')
            response = make_response(redirect(url_for('products.index')))
        response.delete_cookie('basket')
        return response
    else:
        form.process(obj=current_user)
    return render_template("basket/index.html", basket=basket_, products=products, form=form)


@basket.route("/basket/order/<order_token>")
def order(order_token):
    try:
        order_id = confirm_token(order_token)
    except:
        flash('Замовлення не знайдено.', 'danger')
        return redirect(url_for('products.index'))
    order_ = Order.query.get(order_id)
    return render_template("basket/order_info.html", order=order_, order_token=order_token)
