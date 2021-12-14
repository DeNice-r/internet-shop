from app import db
from flask import render_template, redirect, flash, request, url_for, abort, Blueprint
from admin_forms import *
from flask_login import current_user
from models.user import User
from models.product import Product
from functools import wraps
from werkzeug.security import generate_password_hash
from controllers.auth_controller import generate_confirmation_token
from utils import send_email

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
@role_required('admin')
def product():
    return 'Ok', 200


@admin.route("/admin/news", methods=('GET', 'POST'))
@role_required('editor')
def news():
    n = None  # News.query.all()
    return render_template('admin/news.html', news=n)


@admin.route("/admin/support", methods=('GET', 'POST'))
@role_required('support')
def support():
    return render_template('admin/support.html')


@admin.route("/admin/users", methods=('GET', 'POST'))
@role_required('admin')
def users():
    get = request.args
    u = User.query
    if get.get('id'):
        u = u.get(get['id'])
    if get.get('username'):
        u = u.filter(User.username.contains(get['username']))
    if get.get('email'):
        u = u.filter(User.email.contains(get['email']))
    if get.get('firstname'):
        u = u.filter(User.firstname.contains(get['firstname']))
    if get.get('phone'):
        u = u.filter(User.phone.contains(get['phone']))
    if get.get('settlement'):
        u = u.filter(User.settlement.contains(get['settlement']))
    if get.get('address'):
        u = u.filter(User.address.contains(get['address']))
    if get.get('confirmed'):
        u = u.filter(User.confirmed == (get['confirmed'] == '+'))
    if get.get('roles'):
        r = []
        for user_ in u:
            if get['roles'] in str(user_.roles):
                r.append(user_)
        u = r
    if get.get('registered_on'):
        r = []
        for user_ in u:
            if get['registered_on'] in str(user_.registered_on):
                r.append(user_)
        u = r
    if get.get('last_login'):
        r = []
        for user_ in u:
            if get['last_login'] in str(user_.last_login):
                r.append(user_)
        u = r

    if u == User.query:
        u = u.all()
    return render_template('admin/users.html', users=u)


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
                    flash(f'При оновленні виникла помилка: {e}', 'danger')
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
