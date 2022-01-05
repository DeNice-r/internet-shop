from flask import render_template, Blueprint, request, jsonify
from models.post import Post
from math import ceil


posts = Blueprint('posts', __name__)


@posts.route("/posts")
def index():
    return render_template("posts/index.html")


@posts.route("/api/posts", methods=('POST',))
def get_news():
    p = Post.query
    items_per_page = 10
    page = request.headers.get('page')
    number_of_pages = ceil(p.count() / items_per_page)
    # Якщо сторінка більше за кількість сторінок або сторінку не задано - відображаємо першу (0) сторінку
    page = 0 if not page or number_of_pages < int(page) else int(page) - 1
    p = p.order_by(Post.created.asc()).offset(items_per_page * page).limit(items_per_page).all()

    return jsonify({'content': render_template("posts/posts_response.html",
                                               posts=p),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@posts.route("/posts/<int:post_id>", methods=('GET', 'POST'))
def post(post_id: int):
    return render_template("posts/post.html", post=Post.query.get(post_id))
