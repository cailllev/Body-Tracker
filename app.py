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

    stats = get_stats(session[auth_user])
    return render_template("index.html", stats=stats)


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

    date = int(time())
    weight = request.form.get("weight")
    body_fat = request.form.get("body_fat")
    water = request.form.get("water")
    muscle = request.form.get("muscle")
    if not all(e for e in [weight, body_fat, water, muscle]):
        return render_template("add.html", error="Values cannot be Null")

    weight *= 1000  # kg to g
    body_fat, water, muscle = body_fat*10, water*10, muscle*10  # procent to promille
    add_stats(session[auth_user], date, weight, body_fat, water, muscle)
    return redirect("/")
