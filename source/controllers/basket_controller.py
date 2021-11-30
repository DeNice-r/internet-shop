from app import app
from flask import render_template


@app.route("/basket")
def basket():
    return render_template("basket/basket.html")
