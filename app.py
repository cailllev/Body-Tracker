from datetime import datetime
from flask import Flask, redirect, render_template, request, session
from secrets import token_bytes
from time import time

from db import db_login, db_register, get_stats, add_stats

app = Flask(__name__)
app.secret_key = token_bytes(16)
auth_user = "user"


@app.route("/")
def index():
    if auth_user not in session:
        return redirect("/login")

    headers = ["Date", "Weight", "% Body Fat", "% Water", "% Muscles"]
    stats = get_stats(session[auth_user])

    all_stats = []
    labels = []
    weights = []
    for row in stats:
        date, weight, body_fat, water, muscles = row
        date = datetime.fromtimestamp(date).strftime('%d-%m-%Y')

        # TODO refactor
        labels.append(date)
        weights.append(round(weight / 1000, 1))

        weight = str(round(weight / 1000, 1)) + " kg"
        body_fat = str(round(body_fat / 10, 1)) + " %"
        water = str(round(water / 10, 1)) + " %"
        muscles = str(round(muscles / 10, 1)) + " %"
        all_stats.append((date, weight, body_fat, water, muscles))

    return render_template("index.html", headers=headers, stats=all_stats, labels=labels, weights=weights)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    if username and password and db_register(username, password):
        session[auth_user] = username
        return redirect("/")
    return render_template("register.html", error="Username already taken")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    if username and password and db_login(username, password):
        session[auth_user] = username
        return redirect("/")
    return render_template("login.html", error="Username or Password wrong")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    if request.method == "GET":
        return render_template("add.html")

    if auth_user not in session:
        return redirect("/login")

    date = int(time())
    weight = request.form.get("weight")
    body_fat = request.form.get("body_fat")
    water = request.form.get("water")
    muscles = request.form.get("muscles")
    if not all(e for e in [weight, body_fat, water, muscles]):
        return render_template("add.html", error="Values cannot be Null")

    try:
        weight, body_fat, water, muscles = float(weight), float(body_fat), float(water), float(muscles)
    except ValueError:
        return render_template("add.html", error="Values must be Numbers")

    weight = int(weight*1000)  # kg to g
    body_fat, water, muscles = int(body_fat*10), int(water*10), int(muscles*10)  # procent to promille
    add_stats(session[auth_user], date, weight, body_fat, water, muscles)
    return redirect("/")
