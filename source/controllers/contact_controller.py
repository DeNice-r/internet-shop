from app import db
from flask import render_template, Blueprint, request, flash
from forms import AppealForm
from models.appeal import Appeal


contact = Blueprint('contact', __name__)


@contact.route("/contact", methods=('GET', 'POST'))
def index():
    form = AppealForm()
    if form.validate_on_submit():
        try:
            appeal = Appeal(
                form.title.data,
                form.content.data,
                form.firstname.data,
                form.phone.data,
                form.email.data,
            )
            db.session.add(appeal)
            db.session.commit()
        except BaseException as e:
            flash(f'При оновленні виникла помилка: {e}', 'danger')
        else:
            flash(f'Звернення успішно створено з ID #{appeal.id}.', 'success')
    return render_template("contact/index.html", form=form)
