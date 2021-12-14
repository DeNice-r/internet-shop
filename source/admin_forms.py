from flask_wtf import FlaskForm
from wtforms import StringField, TelField, EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, DataRequired, Optional, Length, EqualTo


class UserForm(FlaskForm):
    username = StringField('Назва профіля', validators=[DataRequired("Назва профіля - обов'язкове поле!"),
                                                        Length(4, 50, "Назва профіля недопустимої довжини! (допустима "
                                                                      "довжина від 4 до 50 символів).")])
    email = EmailField('Електронна пошта', validators=[DataRequired("Електронна пошта - обов'язкове поле!"),
                                                       Length(5, 320, "Пошта недопустимої довжини! (допустима "
                                                                      "довжина від 5 до 320 символів)")])
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