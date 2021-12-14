from flask import render_template, Blueprint


contact = Blueprint('contact', __name__)


@contact.route("/contact")
def index():
    return render_template("contact/index.html")
