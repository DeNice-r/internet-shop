import datetime
from flask import render_template, Blueprint, request, make_response, abort, flash, redirect, url_for, session, jsonify
from flask_login import current_user
from models.product import Product
from models.order import Order
from models.cart import Cart
from forms import OrderForm
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm.attributes import flag_modified
from app import app, db


cart = Blueprint('cart', __name__)


def generate_order_token(order_id):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(str(order_id), salt=app.config['SECURITY_PASSWORD_SALT'])


@cart.route("/cart", methods=('GET', 'POST'))
def index():
    cart_ = Cart.query.get(session['_id'])

    form = OrderForm()

    if form.validate_on_submit():
        order_changed = False
        for p in cart_.items:
            product_ = Product.query.get(p)
            if product_.stock < cart_.items[p]:
                cart_.items[p] = product_.stock
                order_changed = True
        response = None
        try:
            order_ = Order(
                request.form.get('comment'),
                form.phone.data,
                form.firstname.data,
                form.settlement.data,
                form.address.data,
                cart_.items
            )
            if current_user.is_authenticated:
                order_.customer = current_user.id
            if order_changed:
                flash('Замовлення змінено у відповідності із наявністю товару на складі.', 'warning')
            db.session.add(order_)
            db.session.commit()
            response = make_response(redirect(url_for('order.get_order', order_token=generate_order_token(order_.id))))
        except ValueError as e:
            flash('Виникла помилка. Будь-ласка спробуйте повторити замовлення.' + str(e), 'danger')
            response = make_response(redirect(url_for('products.index')))
        db.session.delete(cart_)
        db.session.commit()
        return response
    else:
        form.process(obj=current_user)
    return render_template("cart/index.html", form=form)


@cart.route('/api/cart/<action>/<product_id>/<int:value>')
@cart.route('/api/cart/<action>/<product_id>', defaults={'value': 0})
@cart.route('/api/cart/<action>', defaults={'product_id': '-1', 'value': 0})
@cart.route('/api/cart', defaults={'action': 'get', 'product_id': '-1', 'value': 0})
def cart_api(action, product_id, value):
    cart_ = Cart.query.get(session['_id'])
    response = None
    match action:
        case 'set':
            product_ = Product.query.get(product_id)
            if product_ and product_.stock >= value:
                cart_.items[product_id] = value
        case 'add':
            product_ = Product.query.get(product_id)
            if product_id in cart_.items:
                if product_ and product_.stock >= cart_.items[product_id] + value:
                    cart_.items[product_id] += value
            else:
                cart_.items[product_id] = value
        case 'del':
            if product_id == '-1':
                cart_.items = {}
                cart_.created = datetime.datetime.now()
            else:
                cart_.items[product_id] -= value
                if value == 0 or cart_.items[product_id] == 0:
                    del cart_.items[product_id]
        case 'get':
            return jsonify(render_template('cart/cart_response.html', items=cart_.items, product_query=Product.query))
        case _:
            abort(404)

    flag_modified(cart_, 'items')
    db.session.commit()
    return make_response()
