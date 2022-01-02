from __future__ import annotations
from app import app, mail
from flask import request, flash, abort
from urllib.parse import urlparse, urljoin
from flask_mail import Message
from secrets import token_urlsafe
import os
import random
import string


token_64_sample = string.ascii_letters + string.digits + '-_'


class UploadTypes:
    product_upload = 'PRODUCT_UPLOAD'



def token_64(n: int = 16):
    return ''.join(random.choices(token_64_sample, k=n))


def is_picture(filename: str):
    # Перевіряємо, чи картинка прийнятна по її розширенню
    if '.' in filename:
        split = filename.rsplit('.', 1)
        if len(split) == 2:
            return split[1].lower() in app.config['PICTURE_EXTENSIONS']
    return False


def secure_save_image(image, upload_type: str) -> str:
    # якщо картинка підходить
    if is_picture(image.filename):
        # завантажуємо її
        # Для початку, отримуємо розширення
        ext = image.filename.split('.')[-1]
        # Створюємо випадкове ім'я файлу (на випадок не безпечного імені файлу або кількох файлів з одним ім'ям)
        filename = token_64() + '.' + ext
        path = app.config[upload_type + '_FOLDER'] + filename
        # Якщо ім'я зайняте, створюємо нове поки воно не буде унікальним
        while os.path.isfile(path):
            filename = token_urlsafe(16) + '.' + ext
            path = app.config[upload_type + '_FOLDER'] + filename
        # коли знайшли підходяще ім'я, зберігаємо картинку з цим іменем та повертаємо ім'я файла
        image.save('static/' + path)
        return path.split('/')[-1]


def secure_save_images(images: list, upload_type) -> list:
    r = []
    for image in images:
        path = secure_save_image(image, upload_type)
        if path:
            r.append(path)
    return r


def secure_remove_image(filename: str, upload_type: str) -> None:
    # Якщо файл існує
    if os.path.isfile('static/' + app.config[upload_type + '_FOLDER'] + filename):
        # То видаляємо його
        os.remove('static/' + app.config[upload_type + '_FOLDER'] + filename)
    else:
        # У іншому випадку виводимо повідомлення про те, що нічого видаляти
        flash('Файл не існує на сервері.', 'alert alert-danger')


def is_url_safe(target: str):
    if target is None:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def send_email(to: str | list, subject: str, template: str):
    msg = Message(
        subject,
        recipients=to if isinstance(to, list) else [to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


