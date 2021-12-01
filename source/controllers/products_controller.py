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

    # p = Product("Амогус портфель молодіжний", "['amogus-portfel.jpg']", 333.33, 33.03, 4,
    #             "{"
    #             "'крутість': 'крутий шо капєц',"
    #             "'об\'єм': 'ну думаю літри 3-4 буде',"
    #             "'розміри': 'та на дитя налізе навєрно'"
    #             "}", "Ну класний молодіжний портфель. Було б мені 0 років, купив би собі такий теж щоб пофлєксить "
    #                  "перед однокласниками.")
    # db.session.add(p)
    # db.session.commit()

    products = Product.query.order_by('id').limit(items_per_page).offset(page * items_per_page).all()

    if not products:
        abort(404)

    return render_template("products/products.html",
                           products=products,
                           number_of_pages=ceil(Product.query.count() / items_per_page),
                           page=page+1
                           )


@app.route("/product/<int:id>")
def product(id: int):
    return render_template("products/product.html", product=Product.query.get(id), json=json)
