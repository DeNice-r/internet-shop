from app import app, mail
from flask import request, flash, abort
from urllib.parse import urlparse, urljoin
from flask_mail import Message
from functools import wraps
from flask_login import current_user


def is_picture(filename: str):
    if '.' in filename:
        split = filename.rsplit('.', 1)
        if len(split) == 2:
            return split[1].lower() in app.config['PICTURE_EXTENSIONS']
    return False


def bn_to_br(text: str):
    return text.split('\r\n')


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


