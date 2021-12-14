from flask import render_template, request, Blueprint
from flask_login import current_user
from models.product import Product
from math import ceil


products = Blueprint('products', __name__)


@products.route("/products")
def index():
    return render_template("products/index.html")


@products.route("/api/get_products", methods=('POST',))
def get_products():
    # time.sleep(1)
    items_per_page = 8
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


@products.route("/product/<int:product_id>", methods=('GET', 'POST'))
def product(product_id: int):
    print(request.method)
    if request.method == 'POST' and current_user.has_role('editor'):
        # print(request.form.get('pictures'))
        # print(request.form['cock'])
        print(request.form.to_dict())
        print(request.files.getlist('pictures'))
        # pics = request.headers.get('pictures')
        # for p in pics:
        #     print(p)
    return render_template("products/product.html", product=Product.query.get(product_id))


@products.route("/api/product/<int:product_id>", methods=('POST',))
def api_product(product_id: int):
    return render_template("products/product.html", product=Product.query.get(product_id))


@products.route("/api/get_product/<int:product_id>")
def get_product(product_id: int):
    return Product.query.get(product_id).as_json_response()
