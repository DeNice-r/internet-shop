from flask_wtf import FlaskForm
from wtforms import StringField, TelField, EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, DataRequired, Optional, Length, EqualTo  # , Email


class RegisterForm(FlaskForm):
    # TODO: дописати гарні пояснення до помилок
    username = StringField('Назва профіля', validators=[DataRequired("Назва профіля - обов'язкове поле!"),
                                                        Length(4, 50, "Назва профіля недопустимої довжини! (допустима "
                                                                      "довжина від 4 до 50 символів)")])
    email = EmailField('Електронна пошта', validators=[DataRequired("Електронна пошта - обов'язкове поле!"),
                                                       # Email(check_deliverability=True),
                                                       Length(5, 320)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(8), EqualTo('confirm_password',
                                                                                       'Паролі повинні співпадати')])
    confirm_password = PasswordField('Підтвердження пароля', validators=[InputRequired(), Length(8)])
    phone = TelField('Мобільний телефон', validators=[Optional(), Length(9, 13)])
    firstname = StringField("Ім'я", validators=[Optional(), Length(max=50)])
    settlement = StringField('Населений пункт', validators=[Optional(), Length(max=50)])
    address = StringField('Адреса доставки', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Зареєструватися')


class LoginForm(FlaskForm):
    # TODO: дописати гарні пояснення до помилок
    username = StringField('Назва профіля', validators=[DataRequired("Назва профіля - обов'язкове поле!"),
                                                        Length(4, 50, "Назва профіля недопустимої довжини! (допустима "
                                                                      "довжина від 4 до 50 символів)")])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(8)])
    remember_me = BooleanField("Запам'ятати мене")
    submit = SubmitField('Увійти')


class ProfileForm(FlaskForm):
    # TODO: дописати гарні пояснення до помилок
    old_password = PasswordField('Старий пароль', validators=[Optional(), Length(8)])
    new_password = PasswordField('Новий Пароль', validators=[Optional(), Length(8),
                                                             EqualTo('confirm_password', 'Паролі повинні співпадати')])
    confirm_password = PasswordField('Підтвердження пароля', validators=[Optional(), Length(8)])
    phone = TelField('Мобільний телефон', validators=[Optional(), Length(9, 13)])
    firstname = StringField("Ім'я", validators=[Optional(), Length(max=50)])
    settlement = StringField('Населений пункт', validators=[Optional(), Length(max=50)])
    address = StringField('Адреса доставки', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Зберегти')


class ForgotPasswordForm(FlaskForm):
    # TODO: дописати гарні пояснення до помилок
    email = EmailField('Електронна пошта', validators=[InputRequired("Електронна пошта - обов'язкове поле!"),
                                                       # Email(check_deliverability=True),
                                                       Length(5, 320)])
    submit = SubmitField('Надіслати лист')


class ChangePasswordForm(FlaskForm):
    # TODO: дописати гарні пояснення до помилок
    new_password = PasswordField('Новий Пароль', validators=[InputRequired(), Length(8),
                                                             EqualTo('confirm_password', 'Паролі повинні співпадати')])
    confirm_password = PasswordField('Підтвердження пароля', validators=[InputRequired(), Length(8)])
    submit = SubmitField('Надіслати лист')


# TODO: наслідування форм (наприклад, пароль-повтор пароля)
