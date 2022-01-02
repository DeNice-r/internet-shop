import json
import random
import time

from app import db
from flask import render_template, redirect, flash, request, url_for, abort, Blueprint, jsonify
from admin_forms import *
from flask_login import current_user
from models.user import User
from models.product import Product
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
    return render_template('admin/index.html')


@admin.route("/admin/products", methods=('GET', 'POST'))
@role_required('seller')
def products():
    get = request.args
    p = Product.query
    if get.get('id'):
        p = p.get(get.get('id'))
    if get.get('title'):
        p = p.filter(User.title.contains(get.get('title')))
    if get.get('desc'):
        p = p.filter(User.desc.contains(get.get('desc')))
    if get.get('price'):
        p = p.filter(User.price == float(get.get('price')))
    if get.get('discount'):
        p = p.filter(User.discount == float(get.get('discount')))
    if get.get('stock'):
        p = p.filter(User.stock == int(get.get('stock')))
    if get.get('updated'):
        r = []
        for product_ in p:
            if get.get('updated') in str(product_.updated):
                r.append(product_)
        p = r
    if get.get('specs'):
        r = []
        for product_ in p:
            if product_.in_specs(get.get('specs')):
                r.append(product_)
        p = r
    if p == User.query:
        p = p.all()
    return render_template('admin/products.html', products=p)


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


@admin.route("/admin/news", methods=('GET', 'POST'))
@role_required('editor')
def news():
    n = None  # News.query.all()
    return render_template('admin/news.html', news=n)


@admin.route("/admin/support", methods=('GET', 'POST'))
@role_required('support')
def support():
    return render_template('admin/support.html')


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
        u = u.get(search['id'])
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

    if u == User.query:
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
                db.session.commit()
            except BaseException as e:
                flash(f'При оновленні виникла помилка: {e}', 'danger')
            else:
                flash('Дані користувача успішно змінено.', 'success')
            return redirect(url_for('.users'))
        else:
            form.process(obj=user_)
        return render_template('admin/user.html', user=user_, form=form)
    abort(404)
