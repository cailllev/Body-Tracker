from flask import Flask, redirect, render_template, request, session
from db import init, db_login, db_register, get_stats, add_stats
from time import time

app = Flask(__name__)
auth_user = "user"


@app.route("/")
def index():
    if auth_user not in session and not session[auth_user]:
        return redirect("/login")

    stats = get_stats(session[auth_user])
    return render_template("index.html", stats=stats)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    if username and password and db_login(username, password):
        session[auth_user] = username
        return redirect("/")
    return render_template("login.html")


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
    add_stats(session[auth_user], date, weight, body_fat, water, muscle)
    return redirect("/")
