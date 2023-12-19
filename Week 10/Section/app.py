import random

from cs50 import SQL
from flask import Flask, render_template, request

from helpers import random_string

app = Flask(__name__)

db = SQL("sqlite:///history.db")

app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        page = request.form.get("page")

        # Validate user input
        try:
            page = int(page)
        except ValueError:
            return render_template("index.html", placeholder="Enter a valid number", name="Murithi")

        if page < 0:
            return render_template("index.html", placeholder="Enter a valid positive number", name="Murithi")

        db.execute("INSERT INTO history (page) VALUES (?)",page)
        random.seed(page)

    string = random_string(1000)
    rows = db.execute("SELECT page FROM history")
    return render_template("index.html", placeholder=string, history=rows)

