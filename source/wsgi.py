from app import app, db

# Контроллери
from controllers.main_controller import main
from controllers.auth_controller import auth
from controllers.products_controller import products
from controllers.basket_controller import basket
from controllers.news_controller import news
from controllers.contact_controller import contact
from controllers.admin_controller import admin
import controllers.error_controller

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(products)
app.register_blueprint(basket)
app.register_blueprint(news)
app.register_blueprint(contact)
app.register_blueprint(admin)
# app.register_blueprint(error)


# Моделі
import models.user
import models.product
import models.post
import models.order
import models.appeal


debug = app.config['DEBUG']
# Задаємо порт. У режимі відладки порт подвоюється (наприклад для 80 стає 8080)
db.create_all()

if __name__ == '__main__':
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=app.config["PORT"],
    )
