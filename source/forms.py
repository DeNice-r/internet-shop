from flask_wtf import FlaskForm
from wtforms import StringField, TelField, EmailField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Optional, Length, EqualTo  # , Email


class RegisterForm(FlaskForm):
    username = StringField('Назва профіля', validators=[DataRequired("Назва профіля - обов'язкове поле!"),
                                                        Length(4, 50, "Назва профіля недопустимої довжини! (допустима "
                                                                      "довжина від 4 до 50 символів).")])
    email = EmailField('Електронна пошта', validators=[DataRequired("Електронна пошта - обов'язкове поле!"),
                                                       Length(5, 320, "Пошта недопустимої довжини! (допустима "
                                                                      "довжина від 5 до 320 символів)")])
    password = PasswordField('Пароль', validators=[InputRequired("Пароль - обов'язкове поле!"),
                                                   Length(8, 64, "Пароль недопустимої довжини! (допустима "
                                                                 "довжина від 8 до 64 символів)."),
                                                   EqualTo('confirm_password', 'Паролі повинні співпадати.')])
    confirm_password = PasswordField('Підтвердження пароля', validators=[InputRequired("Повтор пароля - обов'язкове "
                                                                                       "поле!"),
                                                                         Length(8, 64)])
    phone = TelField('Мобільний телефон', validators=[Optional(),
                                                      Length(9, 13, "Телефон недопустимої довжини! (допустима "
                                                                    "довжина від 9 до 13 символів).")])
    firstname = StringField("Ім'я", validators=[Optional(), Length(0, 50, "Ім'я недопустимої довжини! (допустима "
                                                                          "довжина до 50 символів).")])
    settlement = StringField('Населений пункт', validators=[Optional(),
                                                            Length(0, 50, "Назва населеного пункту недопустимої "
                                                                          "довжини! (допустима довжина від до 50 "
                                                                          "символів). Для реєстрації зв'яжіться з "
                                                                          "підтримкою.")])
    address = StringField('Адреса доставки', validators=[Optional(),
                                                         Length(0, 200, "Адреса недопустимої довжини! (допустима "
                                                                        "довжина до 200 символів). Для реєстрації "
                                                                        "зв'яжіться з підтримкою.")])
    submit = SubmitField('Зареєструватися')


class LoginForm(FlaskForm):
    username = StringField('Назва профіля', validators=[DataRequired("Назва профіля - обов'язкове поле!"),
                                                        Length(4, 50, "Назва профіля недопустимої довжини! (допустима "
                                                                      "довжина від 4 до 50 символів).")])
    password = PasswordField('Пароль', validators=[DataRequired("Пароль - обов'язкове поле!"),
                                                   Length(8, 64, "Пароль недопустимої довжини! (допустима довжина від 8"
                                                                 " до 64 символів).")])
    remember_me = BooleanField("Запам'ятати мене")
    submit = SubmitField('Увійти')


class ProfileForm(FlaskForm):
    old_password = PasswordField('Старий пароль', validators=[Optional(),
                                                              Length(8, 64, "Старий пароль недопустимої довжини! (допус"
                                                                            "тима довжина від 8 до 64 символів).")])
    new_password = PasswordField('Новий Пароль', validators=[Optional(),
                                                             Length(8, 64, "Новий пароль недопустимої довжини! "
                                                                           "(допустима довжина від 8 до 64 символів)."),
                                                             EqualTo('confirm_password', 'Паролі повинні співпадати!')])
    confirm_password = PasswordField('Підтвердження пароля', validators=[Optional(), Length(8, 64)])
    phone = TelField('Мобільний телефон', validators=[Optional(),
                                                      Length(9, 13, "Телефон недопустимої довжини! (допустима довжина "
                                                                    "від 9 до 13 символів).")])
    firstname = StringField("Ім'я", validators=[Optional(), Length(0, 50, "Ім'я недопустимої довжини! (допустима "
                                                                          "довжина до 50 символів).")])
    settlement = StringField('Населений пункт', validators=[Optional(),
                                                            Length(0, 50, "Назва населеного пункту недопустимої "
                                                                          "довжини! (допустима довжина від до 50 "
                                                                          "символів). Для зміни даних зв'яжіться з "
                                                                          "підтримкою.")])
    address = StringField('Адреса доставки', validators=[Optional(),
                                                         Length(0, 200, "Адреса недопустимої довжини! (допустима "
                                                                        "довжина до 200 символів). Для зміни даних "
                                                                        "зв'яжіться з підтримкою.")])
    submit = SubmitField('Зберегти')


class ForgotPasswordForm(FlaskForm):
    email = EmailField('Електронна пошта', validators=[InputRequired("Електронна пошта - обов'язкове поле!"),
                                                       Length(5, 320, "Пошта недопустимої довжини! (допустима "
                                                                      "довжина від 5 до 320 символів)")])
    submit = SubmitField('Надіслати лист')


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('Новий Пароль', validators=[InputRequired(),
                                                             Length(8, 64, "Пошта недопустимої довжини! (допустима "
                                                                           "довжина від 8 до 64 символів)"),
                                                             EqualTo('confirm_password', 'Паролі повинні співпадати!')])
    confirm_password = PasswordField('Підтвердження пароля', validators=[InputRequired(), Length(8, 64)])
    submit = SubmitField('Надіслати лист')


class OrderForm(FlaskForm):
    firstname = StringField("Ім'я", validators=[DataRequired(),
                                                Length(1, 50, "Ім'я недопустимої довжини! (допустима "
                                                              "довжина до 50 символів).")])
    phone = TelField('Мобільний телефон', validators=[DataRequired(),
                                                      Length(9, 13, "Телефон недопустимої довжини! (допустима довжина "
                                                                    "від 9 до 13 символів).")])
    settlement = StringField('Населений пункт', validators=[DataRequired(),
                                                            Length(1, 50, "Назва населеного пункту недопустимої "
                                                                          "довжини! (допустима довжина від до 50 "
                                                                          "символів).")])
    address = StringField('Адреса доставки', validators=[DataRequired(),
                                                         Length(1, 200, "Адреса недопустимої довжини! (допустима "
                                                                        "довжина до 200 символів).")])
    comment = TextAreaField('Коментар', validators=[Optional(),
                                                    Length(0, 500, "Коментар недопустимої довжини! "
                                                                   "(допустима довжина до 500 символів).")])
    submit = SubmitField('Зберегти')


class AppealForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired("Заголовок звернення - обов'язкове поле!"),
                                                 Length(1, 256, "Назва товару недопустимої довжини! (допустима "
                                                                "довжина від 1 до 256 символів).")])
    content = TextAreaField('Текст', validators=[DataRequired("Текст звернення - обов'язкове поле!")])
    firstname = StringField("Ім'я", validators=[Optional(), Length(0, 50, "Ім'я недопустимої довжини! (допустима "
                                                                          "довжина до 50 символів).")])
    email = EmailField('Електронна пошта', validators=[Optional(),
                                                       Length(5, 320, "Пошта недопустимої довжини! (допустима "
                                                                      "довжина від 5 до 320 символів)")])
    phone = TelField('Мобільний телефон', validators=[Optional(),
                                                      Length(9, 13, "Телефон недопустимої довжини! (допустима "
                                                                    "довжина від 9 до 13 символів).")])
    submit = SubmitField('Надіслати')


# TODO: наслідування форм (наприклад, пароль-повтор пароля або додаткові поля у реєстрації та профілі)
