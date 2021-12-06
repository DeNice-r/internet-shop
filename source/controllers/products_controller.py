import json
import time

from app import app, db
from flask import render_template, abort, request, jsonify
from models.product import Product
from math import ceil


@app.route("/old/products", defaults={'page': 1})
@app.route("/old/products/<int:page>")
def old_products(page: int):
    items_per_page = 8
    page -= 1

    product_list = Product.query.order_by(Product.stock.desc(), Product.id.desc()).limit(items_per_page).offset(
        page * items_per_page).all()

    if not product_list:
        abort(404)

    return render_template("products/old_products.html",
                           products=product_list,
                           number_of_pages=ceil(Product.query.count() / items_per_page),
                           page=page + 1
                           )


@app.route("/products")
def products():
    return render_template("products/ajax_products.html")


@app.route("/api/get_products", methods=('POST',))
def get_products():
    # time.sleep(1)
    items_per_page = 6
    page = request.headers.get('page')
    page = int(page) - 1 if page else 0
    product_list = Product.query.order_by(Product.stock.desc(), Product.id.desc()).limit(items_per_page).offset(
        page * items_per_page).all()

    if not product_list:
        product_list = Product.query.order_by(Product.stock.desc(), Product.id.desc()).limit(items_per_page).all()
        page = 0

    return render_template("products/products_response.html",
                           products=product_list,
                           number_of_pages=ceil(Product.query.count() / items_per_page),
                           page=page + 1)


@app.route("/product/<int:product_id>")
def product(product_id: int):
    return render_template("products/product.html", product=Product.query.get(product_id))


@app.route("/api/get_product/<int:product_id>")
def get_product(product_id: int):
    return Product.query.get(product_id).as_json_response()
