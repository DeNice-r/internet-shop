from flask import render_template, Blueprint, request, jsonify
from models.post import Post
from math import ceil


news = Blueprint('news', __name__)


@news.route("/news")
def index():
    return render_template("news/index.html")


@news.route("/api/news", methods=('POST',))
def get_products():
    p = Post.query
    items_per_page = 10
    page = request.headers.get('page')
    number_of_pages = ceil(p.count() / items_per_page)
    # Якщо сторінка більше за кількість сторінок або сторінку не задано - відображуємо першу (0) сторінку
    page = 0 if not page or number_of_pages < int(page) else int(page) - 1
    p = p.offset(items_per_page * page).limit(items_per_page).all()

    return jsonify({'content': render_template("news/news_response.html",
                                               products=p),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})
