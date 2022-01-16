from flask import render_template, request, Blueprint, jsonify, redirect, url_for, session
from models.product import Product
from math import ceil
from multidict import MultiDict
import json
from sqlalchemy import or_, func, asc, desc
from urllib.parse import unquote

products = Blueprint('products', __name__)


@products.route('/')
def slash_redirect():
    return redirect(url_for('.index'))


@products.route("/products")
def index():
    return render_template("products/index.html")


order_by_values = {'1': 'updated', '2': 'title', '3': 'price', '4': 'discount'}


@products.route("/api/products", methods=('POST',))
def get_products():
    search = MultiDict(json.loads(unquote(request.headers.get('search'))))
    p = Product.query
    if search.get('q'):
        try:
            p = p.filter(or_(Product.id == int(search['q']),
                             func.lower(Product.title).contains(func.lower(search['q'])),
                             func.lower(Product.desc).contains(func.lower(search['q']))))
        except ValueError:
            p = p.filter(or_(func.lower(Product.title).contains(func.lower(search['q'])),
                             func.lower(Product.desc).contains(func.lower(search['q']))))

    if search.get('price_from'):
        p = p.filter(Product.price >= float(search['price_from']))
    if search.get('price_to'):
        p = p.filter((Product.price - Product.discount) <= float(search['price_to']))

    if search.get('order_by'):
        if search.get('order') and search['order'] == '1':
            p = p.order_by(asc(order_by_values[search['order_by']]))
        else:
            p = p.order_by(desc(order_by_values[search['order_by']]))
    else:
        p = p.order_by(Product.updated.desc())

    items_per_page = int(search['items_per_page']) if search.get('items_per_page') else 16
    page = request.headers.get('page')
    number_of_pages = ceil(p.count() / items_per_page)
    # Якщо сторінка більше за кількість сторінок або сторінку не задано - відображуємо першу (0) сторінку
    page = 0 if not page or number_of_pages < int(page) else int(page) - 1
    p = p.offset(items_per_page * page).limit(items_per_page).all()

    return jsonify({'content': render_template("products/products_response.html",
                                               products=p),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@products.route("/product/<int:product_id>", methods=('GET', 'POST'))
def product(product_id: int):
    return render_template("products/product.html", product=Product.query.get(product_id))
