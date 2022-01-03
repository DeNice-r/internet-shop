from flask_wtf import FlaskForm
from wtforms import StringField, TelField, EmailField, PasswordField, SubmitField, IntegerField, TextAreaField,\
    MultipleFileField, FloatField, HiddenField, FileField
from wtforms.validators import DataRequired, Optional, Length, EqualTo


class UserForm(FlaskForm):
    username = StringField('Назва профіля', validators=[DataRequired("Назва профілю - обов'язкове поле!"),
                                                        Length(4, 50, "Назва профілю недопустимої довжини! (допустима "
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


class ProductForm(FlaskForm):
    title = StringField('Назва товару', validators=[DataRequired("Назва товару - обов'язкове поле!"),
                                                    Length(1, 256, "Назва товару недопустимої довжини! (допустима "
                                                                   "довжина від 1 до 256 символів).")])
    desc = TextAreaField('Опис')
    pictures = HiddenField()
    new_pictures = MultipleFileField('Картинки')
    price = FloatField('Ціна', default=0.)
    discount = FloatField('Знижка', default=0.)
    stock = IntegerField('В наявності', default=1)
    specs = HiddenField()
    submit = SubmitField('Зберегти')


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired("Заголовок новини - обов'язкове поле!"),
                                                 Length(1, 256, "Заголовок новини недопустимої довжини! (допустима "
                                                                "довжина від 1 до 256 символів).")])
    content = TextAreaField('Текст', validators=[DataRequired("Текст новини - обов'язкове поле!")])
    picture = FileField('Картинка')
    submit = SubmitField('Зберегти')
