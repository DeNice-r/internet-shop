from flask import render_template, Blueprint


basket = Blueprint('basket', __name__)


@basket.route("/basket")
def index():
    return render_template("basket/index.html")
