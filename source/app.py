from flask import Flask
from dotenv import load_dotenv
from os import getcwd, environ
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate

# Завантажуємо змінні середовища
load_dotenv()


# Створюємо додаток
app = Flask('KIShop')


# Режим відладки
app.config['DEBUG'] = eval(environ['DEBUG'])
app.config['PORT'] = environ['PORT'] * (int(app.config['DEBUG']) + 1)


# Задаємо домен, якщо працюємо не у режимі відладки
app.config['SERVER_NAME'] = ('curse.c:' + app.config['PORT']) if app.config['DEBUG'] else environ['DOMAIN']


# Секретний ключ (потрібен, наприклад, щоб отримувати POST-запити)
app.config['SECRET_KEY'] = environ['SECRET_KEY']


# Папка, у якій працює програма
app.config['DIR'] = getcwd()


# Папка, де будуть знаходитися доступні користувачу файли
app.config['STATIC_FOLDER'] = '/static/'
# Папка, де будуть збережені картинки
app.config['IMAGE_FOLDER'] = 'image/'
# Папка, де будуть збережені файли користувачів
app.config['UPLOAD_FOLDER'] = 'upload/'
# Папка, де будуть збережені файли товарів
app.config['PRODUCT_UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER'] + 'product/'
# Папка, де будуть збережені файли новин
app.config['POST_UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER'] + 'post/'
# Прийнятні розширення картинок
app.config['PICTURE_EXTENSIONS'] = ['apng', 'avif', 'gif', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png', 'svg', 'webp']


# Конфігурація підключення до бд
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Створення підключення до бд
db = SQLAlchemy(app)
# Створення менеджера міграцій бд
migrate = Migrate(app, db)

# Секретний ключ для хешування паролів
app.config['SECURITY_PASSWORD_SALT'] = environ['SECURITY_PASSWORD_SALT']


# Створення менеджера авторизації
lm = LoginManager(app)

# Конфігурація менеджера авторизації
lm.login_view = '/auth/login'
lm.login_message = 'Ця сторінка доступна лише авторизованим користувачам.'
lm.login_message_category = 'danger'


# Конфігурація менеджера електронних листів
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

# Створення менеджера електронних листів
mail = Mail(app)


# Конфігурація CSRF-захисту
app.config['WTF_CSRF_ENABLED'] = True

# Створення CSRF-захисту для AJAX-запитів
csrf = CSRFProtect(app)

