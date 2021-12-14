from flask import render_template, Blueprint


news = Blueprint('news', __name__)


@news.route("/news")
def index():
    return render_template("news/index.html")
