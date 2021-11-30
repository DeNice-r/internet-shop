from app import app
from flask import render_template


@app.errorhandler(404)
def error(e):
    return render_template("error/404.html")
