import json

from app import app, db
from flask import render_template, abort
from models.product import Product
from math import ceil


@app.route("/products", defaults={'page': 1})
@app.route("/products/<int:page>")
def products(page: int):
    items_per_page = 8
    page -= 1

    products = Product.query.order_by(Product.id.desc()).limit(items_per_page).offset(page * items_per_page).all()

    if not products:
        abort(404)

    return render_template("products/products.html",
                           products=products,
                           number_of_pages=ceil(Product.query.count() / items_per_page),
                           page=page + 1
                           )


@app.route("/product/<int:id>")
def product(id: int):
    return render_template("products/product.html", product=Product.query.get(id), json=json)
