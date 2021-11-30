from app import app, db

# Контроллери
import controllers.index_controller
import controllers.auth_controller
import controllers.products_controller
import controllers.basket_controller
import controllers.news_controller
import controllers.contact_controller
import controllers.error_controller

# Моделі
import models.user
import models.product


is_debug = app.config['DEBUG']
# Задаємо порт. У режимі відладки порт подвоюється (наприклад для 80 стає 8080)
port = app.config["PORT"] * (int(is_debug) + 1)
db.create_all()

app.run(
    debug=is_debug,
    host="0.0.0.0",  # Kinda guarantees that server will be available from outside
    port=port,
)
