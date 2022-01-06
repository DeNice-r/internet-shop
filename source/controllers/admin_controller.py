import json
from app import db
from flask import render_template, redirect, flash, request, url_for, abort, Blueprint, jsonify
from admin_forms import *
from flask_login import current_user
from models.user import User
from models.product import Product
from models.post import Post
from models.appeal import Appeal
from models.order import Order
from functools import wraps
from werkzeug.security import generate_password_hash
from controllers.auth_controller import generate_confirmation_token
from utils import send_email, secure_save_image, secure_save_images, secure_remove_image, UploadTypes
from multidict import MultiDict
from math import ceil
from sqlalchemy.orm.attributes import flag_modified
from urllib.parse import unquote
from sqlalchemy import func

admin = Blueprint('admin', __name__)


def role_required(role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.has_role(role):
                return func(*args, **kwargs)
            abort(401)

        return wrapper

    return decorator


def any_role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.has_any_role(roles):
                return func(*args, **kwargs)
            abort(401)

        return wrapper

    return decorator


@admin.route("/admin", methods=('GET', 'POST'))
@any_role_required(('admin', 'editor', 'support', 'seller'))
def index():
    from app import app
    print(app.config['SERVER_NAME'])
    return render_template('admin/index.html')


@admin.route("/admin/products", methods=('GET',))
@role_required('seller')
def products():
    return render_template('admin/products.html')


@admin.route("/api/admin/products", methods=('POST',))
@role_required('seller')
def get_products():
    search = MultiDict(json.loads(unquote(request.headers.get('search'))))
    p = Product.query
    if search.get('id'):
        p = p.filter(Product.id == int(search['id']))
    if search.get('title'):
        p = p.filter(func.lower(Product.title).contains(func.lower(search['title'])))
    if search.get('desc'):
        p = p.filter(func.lower(Product.desc).contains(func.lower(search['desc'])))
    if search.get('price'):
        p = p.filter(func.lower(Product.price).contains(func.lower(search['price'])))
    if search.get('discount'):
        p = p.filter(func.lower(Product.discount).contains(func.lower(search['discount'])))
    if search.get('stock'):
        p = p.filter(func.lower(Product.stock).contains(func.lower(search['stock'])))
    if search.get('specs'):
        p = p.filter(func.lower(Product.specs).contains(func.lower(search['specs'])))
    if search.get('updated'):
        r = []
        for product_ in p:
            if search['updated'] in str(product_.updated):
                r.append(product_)
        p = r

    if type(p) == type(Product.query):
        p = p.all()

    items_per_page = int(search['items_per_page']) if search.get('items_per_page') else 20
    page = request.headers.get('page')
    page = int(page) - 1 if page else 0

    try:
        is_iterable_test = iter(p)
    except TypeError:
        p = [p]
    try:
        number_of_pages = ceil(len(p) / items_per_page)
    except TypeError:
        number_of_pages = ceil(p.count() / items_per_page)
    p.sort(key=lambda x: x.updated, reverse=True)
    p = p[items_per_page * page:items_per_page * (page + 1)]

    return jsonify({'content': render_template("admin/products_response.html",
                                               products=p),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@admin.route("/admin/product", methods=('GET', 'POST'))
@role_required('seller')
def product():
    product_id = request.args.get('product_id')
    delete = request.args.get('delete')
    form = ProductForm()
    if product_id:
        product_ = Product.query.get(product_id)
        if delete == '1':
            try:
                db.session.delete(product_)
                db.session.commit()
            except BaseException as e:
                flash(f'При видаленні виникла помилка: {e}', 'danger')
            else:
                flash('Товар успішно видалено.', 'success')
            return redirect(url_for('.products'))

        if form.validate_on_submit():
            try:
                product_.title = form.title.data
                product_.price = form.price.data
                product_.discount = form.discount.data
                product_.stock = form.stock.data
                product_.specs = json.loads(form.specs.data)
                product_.desc = form.desc.data

                modified_pictures = form.pictures.data

                pic_index = 0
                while pic_index < len(product_.pictures):
                    if product_.pictures[pic_index] not in modified_pictures:
                        secure_remove_image(product_.pictures[pic_index], UploadTypes.product_upload)
                        del product_.pictures[pic_index]
                    else:
                        pic_index += 1

                pictures = request.files.getlist('new_pictures')
                product_.pictures.extend(secure_save_images(pictures, UploadTypes.product_upload))

                flag_modified(product_, 'pictures')
                db.session.commit()
            except BaseException as e:
                flash(f'При оновленні виникла помилка: {e}', 'danger')
            else:
                flash('Дані товару успішно змінено.', 'success')
            return redirect(url_for('.products'))
        else:
            form.process(obj=product_)
            form.specs.data = json.dumps(product_.specs)
            form.pictures.data = json.dumps(product_.pictures)
        return render_template('admin/product.html', form=form, product=product_)
    elif form.validate_on_submit():
        try:
            pictures = request.files.getlist('new_pictures')
            product_ = Product(
                form.title.data,
                secure_save_images(pictures, UploadTypes.product_upload),
                form.price.data,
                form.discount.data,
                form.stock.data,
                form.specs.data,
                form.desc.data
            )
            db.session.add(product_)
            db.session.commit()
        except BaseException as e:
            flash(f'При оновленні виникла помилка: {e}', 'danger')
        else:
            flash(f'Товар успішно створено з ID #{product_.id}.', 'success')
        return redirect(url_for('.products'))
    return render_template('admin/product.html', form=form)


@admin.route("/admin/posts", methods=('GET',))
@role_required('editor')
def posts():
    return render_template('admin/posts.html')


@admin.route("/api/admin/posts", methods=('POST',))
@role_required('editor')
def get_posts():
    search = MultiDict(json.loads(unquote(request.headers.get('search'))))
    p = Post.query
    if search.get('id'):
        p = p.filter(Post.id == int(search['id']))
    if search.get('title'):
        p = p.filter(func.lower(Post.title).contains(func.lower(search['title'])))
    if search.get('content'):
        p = p.filter(func.lower(Post.content).contains(func.lower(search['content'])))
    if search.get('author'):
        p = p.filter(Post.author == search['author'])
    if search.get('updated'):
        r = []
        for post_ in p:
            if search['updated'] in str(post_.updated):
                r.append(post_)
        p = r
    if search.get('created'):
        r = []
        for post_ in p:
            if search['created'] in str(post_.created):
                r.append(post_)
        p = r

    if type(p) == type(Post.query):
        p = p.all()

    items_per_page = int(search['items_per_page']) if search.get('items_per_page') else 20
    page = request.headers.get('page')
    page = int(page) - 1 if page else 0

    try:
        is_iterable_test = iter(p)
    except TypeError:
        p = [p]
    try:
        number_of_pages = ceil(len(p) / items_per_page)
    except TypeError:
        number_of_pages = ceil(p.count() / items_per_page)
    p.sort(key=lambda x: x.updated, reverse=True)
    p = p[items_per_page * page:items_per_page * (page + 1)]

    return jsonify({'content': render_template("admin/posts_response.html",
                                               posts=p),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@admin.route("/admin/post", methods=('GET', 'POST'))
@role_required('editor')
def post():
    post_id = request.args.get('post_id')
    delete = request.args.get('delete')
    form = PostForm()
    if post_id:
        post_ = Post.query.get(post_id)
        if delete == '1':
            # TODO: видалення через ajax?
            try:
                db.session.delete(post_)
                db.session.commit()
            except BaseException as e:
                flash(f'При видаленні виникла помилка: {e}', 'danger')
            else:
                flash('Новину успішно видалено.', 'success')
            return redirect(url_for('.posts'))

        if form.validate_on_submit():
            try:
                post_.title = form.title.data
                post_.content = form.content.data

                picture = request.files.get('picture')
                new_picture = secure_save_image(picture, UploadTypes.post_upload)
                if new_picture:
                    secure_remove_image(post_.picture, UploadTypes.post_upload)
                    post_.picture = new_picture

                db.session.commit()
            except BaseException as e:
                flash(f'При оновленні виникла помилка: {e}', 'danger')
            else:
                flash('Дані новини успішно змінено.', 'success')
            return redirect(url_for('.posts'))
        else:
            form.process(obj=post_)
        return render_template('admin/post.html', form=form, post=post_)
    elif form.validate_on_submit():
        try:
            picture = request.files.get('picture')
            post_ = Post(
                form.title.data,
                form.content.data,
                secure_save_image(picture, UploadTypes.post_upload)
            )
            db.session.add(post_)
            db.session.commit()
        except BaseException as e:
            flash(f'При оновленні виникла помилка: {e}', 'danger')
        else:
            flash(f'Товар успішно створено з ID #{post_.id}.', 'success')
        return redirect(url_for('.posts'))
    return render_template('admin/post.html', form=form)


@admin.route("/admin/support/appeals", methods=('GET', 'POST'))
@role_required('support')
def appeals():
    return render_template('admin/appeals.html')


@admin.route("/api/admin/support/appeals", methods=('GET', 'POST'))
@role_required('support')
def get_appeals():
    search = MultiDict(json.loads(unquote(request.headers.get('search'))))
    a = Appeal.query
    if search.get('id'):
        a = a.filter(Appeal.id == int(search['id']))
    if search.get('title'):
        a = a.filter(func.lower(Appeal.title).contains(func.lower(search['title'])))
    if search.get('content'):
        a = a.filter(func.lower(Appeal.content).contains(func.lower(search['content'])))
    if search.get('customer'):
        a = a.filter(Appeal.customer == int(search['customer']))
    if search.get('phone'):
        a = a.filter(func.lower(Appeal.phone).contains(func.lower(search['phone'])))
    if search.get('email'):
        a = a.filter(func.lower(Appeal.email).contains(func.lower(search['email'])))
    if search.get('firstname'):
        a = a.filter(func.lower(Appeal.firstname).contains(func.lower(search['firstname'])))
    if search.get('support_comment'):
        a = a.filter(func.lower(Appeal.support_comment).contains(func.lower(search['support_comment'])))
    if search.get('closed'):
        a = a.filter(Appeal.closed == (search['closed'] == '+'))
    if search.get('created'):
        r = []
        for appeal_ in a:
            if search['created'] in str(appeal_.created):
                r.append(appeal_)
        a = r

    if type(a) == type(Appeal.query):
        a = a.all()

    items_per_page = int(search['items_per_page']) if search.get('items_per_page') else 20
    page = request.headers.get('page')
    page = int(page) - 1 if page else 0

    try:
        is_iterable_test = iter(a)
    except TypeError:
        a = [a]
    try:
        number_of_pages = ceil(len(a) / items_per_page)
    except TypeError:
        number_of_pages = ceil(a.count() / items_per_page)
    a.sort(key=lambda x: x.created, reverse=True)
    a = a[items_per_page * page:items_per_page * (page + 1)]

    return jsonify({'content': render_template("admin/appeals_response.html",
                                               appeals=a),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@admin.route("/admin/support/appeal", methods=('GET', 'POST'))
@role_required('support')
def appeal():
    form = AppealForm()
    appeal_id = request.args.get('appeal_id')
    appeal_ = Appeal.query.get(appeal_id)
    if not (appeal_id and appeal_):
        abort(404)
    if form.validate_on_submit():
        print(request.form.get('support_comment'))
        appeal_.support_comment = form.support_comment.data
        appeal_.closed = form.closed.data
        db.session.commit()
        return redirect(url_for('.appeals'))
    else:
        form.support_comment.data = appeal_.support_comment
        form.closed.data = appeal_.closed
    return render_template('admin/appeal.html', form=form, appeal=appeal_)


@admin.route("/admin/support/orders", methods=('GET', 'POST'))
@role_required('support')
def orders():
    return render_template('admin/orders.html')


@admin.route("/api/admin/support/orders", methods=('GET', 'POST'))
@role_required('support')
def get_orders():
    search = MultiDict(json.loads(unquote(request.headers.get('search'))))
    o = Order.query
    if search.get('id'):
        o = o.filter(Order.id == int(search['id']))
    if search.get('customer'):
        o = o.filter(Order.customer == int(search['customer']))
    if search.get('firstname'):
        o = o.filter(func.lower(Order.firstname).contains(func.lower(search['firstname'])))
    if search.get('comment'):
        o = o.filter(func.lower(Order.comment).contains(func.lower(search['comment'])))
    if search.get('phone'):
        o = o.filter(func.lower(Order.phone).contains(func.lower(search['phone'])))
    if search.get('settlement'):
        o = o.filter(func.lower(Order.settlement).contains(func.lower(search['settlement'])))
    if search.get('address'):
        o = o.filter(func.lower(Order.address).contains(func.lower(search['address'])))
    if search.get('final_price'):
        o = o.filter(Order.final_price == int(search['final_price']))
    if search.get('status'):
        r = []
        lower_status = search['status'].lower()
        for order_ in o:
            if lower_status in order_.get_status_string().lower():
                r.append(order_)
        o = r
    if search.get('products'):
        r = []
        for order_ in o:
            if search['products'] in str(order_.products):
                r.append(order_)
        o = r
    if search.get('created'):
        r = []
        for order_ in o:
            if search['created'] in str(order_.created):
                r.append(order_)
        o = r

    if type(o) == type(User.query):
        o = o.all()

    items_per_page = int(search['items_per_page']) if search.get('items_per_page') else 20
    page = request.headers.get('page')
    page = int(page) - 1 if page else 0

    try:
        is_iterable_test = iter(o)
    except TypeError:
        o = [o]
    try:
        number_of_pages = ceil(len(o) / items_per_page)
    except TypeError:
        number_of_pages = ceil(o.count() / items_per_page)
    o.sort(key=lambda x: x.status if x.status >= 0 else 63)  # , reverse=True)
    o = o[items_per_page * page:items_per_page * (page + 1)]

    return jsonify({'content': render_template("admin/orders_response.html",
                                               orders=o),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@admin.route("/admin/support/order", methods=('GET', 'POST'))
@role_required('support')
def order():
    form = OrderForm()
    order_id = request.args.get('order_id')
    order_ = Order.query.get(order_id)
    if not (order_id and order_):
        abort(404)
    if form.validate_on_submit():
        order_.set_status(int(form.status.data))
        db.session.commit()
        return redirect(url_for('.orders'))
    else:
        form.status.data = order_.status
    return render_template('admin/order.html', form=form, order=order_, product_query=Product.query)


@admin.route("/admin/users", methods=('GET',))
@role_required('admin')
def users():
    return render_template('admin/users.html')


@admin.route("/api/admin/users", methods=('POST',))
@role_required('admin')
def get_users():
    search = MultiDict(json.loads(unquote(request.headers.get('search'))))
    u = User.query
    if search.get('id'):
        u = u.filter(User.id == int(search['id']))
    if search.get('username'):
        u = u.filter(func.lower(User.username).contains(func.lower(search['username'])))
    if search.get('email'):
        u = u.filter(func.lower(User.email).contains(func.lower(search['email'])))
    if search.get('firstname'):
        u = u.filter(func.lower(User.firstname).contains(func.lower(search['firstname'])))
    if search.get('phone'):
        u = u.filter(func.lower(User.phone).contains(func.lower(search['phone'])))
    if search.get('settlement'):
        u = u.filter(func.lower(User.settlement).contains(func.lower(search['settlement'])))
    if search.get('address'):
        u = u.filter(func.lower(User.address).contains(func.lower(search['address'])))
    if search.get('confirmed'):
        u = u.filter(User.confirmed == (search['confirmed'] == '+'))
    if search.get('roles'):
        r = []
        for user_ in u:
            if search['roles'] in str(user_.roles):
                r.append(user_)
        u = r
    if search.get('registered_on'):
        r = []
        for user_ in u:
            if search['registered_on'] in str(user_.registered_on):
                r.append(user_)
        u = r
    if search.get('last_login'):
        r = []
        for user_ in u:
            if search['last_login'] in str(user_.last_login):
                r.append(user_)
        u = r

    if type(u) == type(User.query):
        u = u.all()

    items_per_page = int(search['items_per_page']) if search.get('items_per_page') else 20
    page = request.headers.get('page')
    page = int(page) - 1 if page else 0

    try:
        is_iterable_test = iter(u)
    except TypeError:
        u = [u]
    try:
        number_of_pages = ceil(len(u) / items_per_page)
    except TypeError:
        number_of_pages = ceil(u.count() / items_per_page)
    u.sort(key=lambda x: x.registered_on, reverse=True)
    u = u[items_per_page * page:items_per_page * (page + 1)]

    return jsonify({'content': render_template("admin/users_response.html",
                                               users=u),
                    'pagination': render_template('shared/pagination.html',
                                                  number_of_pages=number_of_pages,
                                                  page=page + 1)})


@admin.route("/admin/user", methods=('GET', 'POST'))
@role_required('admin')
def user():
    user_id = request.args.get('user_id')
    delete = request.args.get('delete')
    form = UserForm()
    if user_id:
        user_ = User.query.get(user_id)
        if delete == '1':
            if user_.has_role('admin'):
                flash('Адміністраторів може назначати та видаляти тільки супер-адміністратор. Якщо це дійсно потрібно -'
                      ' зверніться до нього.', 'danger')
            else:
                try:
                    db.session.delete(user_)
                    db.session.commit()
                except BaseException as e:
                    flash(f'При видаленні виникла помилка: {e}', 'danger')
                else:
                    flash('Користувача успішно видалено.', 'success')
            return redirect(url_for('.users'))

        if form.validate_on_submit():
            try:
                user_.username = form.username.data
                if form.email.data and form.email.data != user_.email:
                    user_.email = form.email.data
                    user_.confirmed = False
                    token = generate_confirmation_token(user_.email)
                    confirm_url = url_for('auth.confirm', token=token, _external=True)
                    send_email(user_.email, "Підтвердження пошти",
                               render_template('auth/mails/email_confirmation.html', confirm_url=confirm_url))
                    flash('Пошту успішно змінено. Тепер користувачу необхідно її підтвердити перейшовши по посиланню, '
                          'надісланому на цю пошту.', 'success')
                if form.new_password.data:
                    user_.password = generate_password_hash(form.new_password.data)
                user_.phone = form.phone.data
                user_.firstname = form.firstname.data
                user_.settlement = form.settlement.data
                user_.address = form.address.data
                user_.roles = json.loads(form.roles.data)
                db.session.commit()
            except BaseException as e:
                flash(f'При оновленні виникла помилка: {e}', 'danger')
            else:
                flash('Дані користувача успішно змінено.', 'success')
            return redirect(url_for('.users'))
        else:
            form.process(obj=user_)
            form.roles.data = json.dumps(user_.roles)
        return render_template('admin/user.html', user=user_, form=form)
    abort(404)
