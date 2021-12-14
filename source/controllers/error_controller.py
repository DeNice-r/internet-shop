from app import app
from flask import render_template


def error(e):
    return render_template("error/error.html", error=str(e)[:3])


app.register_error_handler(401, error)
app.register_error_handler(404, error)
