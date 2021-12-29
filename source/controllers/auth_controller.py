import datetime

from app import app, db
from flask import render_template, redirect, flash, request, url_for, Blueprint
from forms import *
from flask_login import current_user, login_user, login_required, logout_user
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from utils import is_url_safe, send_email
from secrets import token_urlsafe
from datetime import timedelta
import sqlalchemy
import re


auth = Blueprint('auth', __name__)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email


@auth.route("/auth/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Ви вже увійшли.', 'warning')
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        check_user = User.query.filter_by(username=form.username.data).first()
        if check_user and check_password_hash(check_user.password, form.password.data):
            if not check_user.confirmed:
                token = generate_confirmation_token(check_user.email + '$' + token_urlsafe(10))
                flash(f'Перед авторизацією потрібно підтвердити пошту. <a href="resend/{token}">Натисніть для відправлення нового листа.</a>', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(check_user, form.remember_me.data, timedelta(14))
            check_user.last_login = datetime.datetime.now()
            db.session.commit()
            next_page = request.args.get('next')

            # Якщо посилання безпечне - переправляємо на нього користувача, інакше - перенаправляємо його на головну
            return redirect(next_page if is_url_safe(next_page) else '/')
        else:
            flash(f'Невірний логін або пароль.', 'danger')
            pass
    return render_template("auth/login.html", form=form)


def validate_username(text: str):
    login_re = r'^[a-zA-Z_0-9]+$'
    return re.fullmatch(login_re, text) is not None


def validate_email(text: str):
    email_re = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b$'
    return re.fullmatch(email_re, text) is not None


@auth.route("/auth/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Ви вже зареєстровані.', 'warning')
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if validate_username(form.username.data) and validate_email(form.email.data):
            new_user = User(form.username.data, form.email.data, generate_password_hash(form.password.data),
                            form.phone.data, form.firstname.data, form.settlement.data, form.address.data)
            try:
                db.session.add(new_user)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                if 'username' in e.args[0]:
                    flash("Користувач з таким ім'ям вже існує.", 'danger')
                elif 'email' in e.args[0]:
                    flash("Користувач з такою поштою вже існує.", 'danger')
                else:
                    raise
                return render_template("auth/register.html", form=form)
            token = generate_confirmation_token(new_user.email)
            confirm_url = url_for('.confirm', token=token, _external=True)
            send_email(new_user.email, "Підтвердження пошти",
                       render_template('auth/mails/email_confirmation.html', confirm_url=confirm_url))
            flash('Реєстрація успішна. Будь-ласка активуйте пошту та авторизуйтеся.', 'success')
            return redirect(url_for('.login'))
        else:
            if not validate_username(form.username.data):
                flash("Ім'я профіля може містити тільки A-Z, a-z, 0-9 та _", 'danger')
            if not validate_email(form.email.data):
                flash("Недійсна пошта.", 'danger')
    return render_template("auth/register.html", form=form)


@auth.route('/auth/confirm/<token>')
def confirm(token):
    try:
        email = confirm_token(token)
    except:
        flash('Посилання для підтвердження пошти помилкове або застаріло.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Пошту вже підтверджено. Будь-ласка, авторизуйтесь.', 'warning')
    else:
        logout_user()
        try:
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
        except:
            flash('Виникла помилка.', 'danger')
        else:
            flash('Пошту успішно підтверджено.', 'success')
    return redirect(url_for('.login'))


@auth.route('/auth/resend/<token>')
def resend_confirmation(token):
    email = confirm_token(token, 60)
    if isinstance(email, str):
        email = email.split('$')[0]
        user = User.query.filter_by(email=email).first_or_404()
        if not user.confirmed:
            token = generate_confirmation_token(email)
            confirm_url = url_for('.confirm', token=token, _external=True)
            html = render_template('auth/mails/email_confirmation.html', confirm_url=confirm_url)
            subject = "Підтвердження пошти"
            send_email(user.email, subject, html)
            flash('Новий лист для підтвердження відправлено.', 'success')
        else:
            flash('Ви вже підтвердили свою пошту.', 'danger')
    else:
        flash('Помилковий код повторної відправки листа.', 'danger')
    return redirect(url_for('.login'))


@auth.route("/auth/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.phone = form.phone.data
        current_user.firstname = form.firstname.data
        current_user.settlement = form.settlement.data
        current_user.address = form.address.data
        if check_password_hash(current_user.password, form.old_password.data)\
                and form.new_password.data != '':
            current_user.password = generate_password_hash(form.new_password.data)
            flash('Пароль успішно змінено.', 'success')
        db.session.commit()
        flash('Дані успішно оновлено.', 'success')
    else:
        form.process(obj=current_user)
    return render_template("auth/profile.html", form=form)


@auth.route('/auth/forgot', methods=['GET', 'POST'])
def forgot_password_send():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            change_url = url_for('.forgot_password_change', token=generate_confirmation_token(user.username), _external=True)
            send_email(user.email, 'Відновлення аккаунта на KIShop', render_template('auth/mails/forgot_password.html',
                                                                                     change_url=change_url))
        flash('Лист з посиланням для відновлення надіслано.', 'success')
        return redirect(url_for('.login'))
    return render_template('auth/forgot_password_send.html', form=form)


@auth.route('/auth/forgot/<token>', methods=['GET', 'POST'])
def forgot_password_change(token):
    form = ChangePasswordForm()
    username = confirm_token(token)
    if isinstance(username, str):
        user = User.query.filter_by(username=username).first_or_404()
        if form.validate_on_submit():
            user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Пароль успішно змінено.', 'success')
            return redirect(url_for('.login'))
        return render_template('auth/forgot_password_change.html', form=form)
    flash('Посилання для відновлення профілю помилкове або застаріло.', 'danger')
    return redirect(url_for('main.index'))


@auth.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
