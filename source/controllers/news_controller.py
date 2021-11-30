from app import app
from flask import render_template


@app.route("/news")
def news():
    return render_template("news/news.html")
