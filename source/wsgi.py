from flask import session
from flask_login import current_user
from app import app, db
from utils import token_64
from models.cart import Cart


# Контроллери
from controllers.auth_controller import auth
from controllers.products_controller import products
from controllers.cart_controller import cart
from controllers.order_controller import order
from controllers.posts_controller import posts
from controllers.contact_controller import contact
from controllers.admin_controller import admin
import controllers.error_controller


app.register_blueprint(auth)
app.register_blueprint(products)
app.register_blueprint(cart)
app.register_blueprint(order)
app.register_blueprint(posts)
app.register_blueprint(contact)
app.register_blueprint(admin)
# app.register_blueprint(error)


# Моделі
import models.user
import models.product
import models.post
import models.order
import models.appeal
import models.cart


debug = app.config['DEBUG']
# Задаємо порт. У режимі відладки порт подвоюється (наприклад для 80 стає 8080)
db.create_all()


@app.before_request
def set_session_id():
    if not session.get('_id'):
        session['_id'] = token_64(128)
    cart_ = Cart.query.get(session['_id'])
    if cart_ and cart_.customer is None and current_user.is_authenticated:
        cart_.customer = current_user.id
    elif not cart_:
        if current_user.is_authenticated:
            cart_ = Cart.query.filter_by(customer=current_user.id).first()
            if cart_:
                cart_.session_id = session['_id']
            else:
                new_cart = Cart(session['_id'])
                db.session.add(new_cart)
        else:
            new_cart = Cart(session['_id'])
            db.session.add(new_cart)
    db.session.commit()


if __name__ == '__main__':
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=app.config["PORT"],
    )
