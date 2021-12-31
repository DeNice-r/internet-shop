from flask import render_template, Blueprint, request, jsonify
from models.post import Post
from math import ceil


posts = Blueprint('posts', __name__)


@posts.route("/posts")
def index():
    return render_template("posts/index.html")


@posts.route("/api/posts", methods=('POST',))
def get_news():
    p = Post.query.all()
    for x in range(15):
        p.extend(p)
    items_per_page = 10
    page = request.headers.get('page')
    number_of_pages = ceil(len(p) / items_per_page)
    page = 0 if not page or number_of_pages < int(page) else int(page) - 1
    p = p[page * items_per_page:items_per_page + page * items_per_page]

    # p = Post.query
    # items_per_page = 10
    # page = request.headers.get('page')
    # number_of_pages = ceil(p.count() / items_per_page)
    # Якщо сторінка більше за кількість сторінок або сторінку не задано - відображуємо першу (0) сторінку
    # page = 0 if not page or number_of_pages < int(page) else int(page) - 1
    # p = p.offset(items_per_page * page).limit(items_per_page).all()

    return jsonify({'content': render_template("posts/posts_response.html",
                                               posts=p),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@posts.route("/posts/<int:post_id>", methods=('GET', 'POST'))
def post(post_id: int):
    return 0  # render_template("products/product.html", product=Post.query.get(post_id))
