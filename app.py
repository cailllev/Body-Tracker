from flask import Flask, redirect, render_template, request, session
from secrets import token_bytes

from db import db_login, db_register, get_stats, add_stats, edit_stats, delete_stats, delete_user, categories
from utils import check_submission, parse_submission, beautify_stats, parse_stats_for_category, get_y_boarder, \
    headers, margin_per_category

app = Flask(__name__)
app.secret_key = token_bytes(16)
auth_user = "user"


@app.route("/")
def index():
    if auth_user not in session:
        return redirect("/login")

    category = request.args.get("cat")  # TODO, frontend
    if not category or category not in categories:
        category = "weight"
    category_label = category.capitalize()

    stats = get_stats(session[auth_user], category)
    round_to = 1  # round all datapoints to 1 decimal
    datapoints, date_labels = parse_stats_for_category(stats, round_to)

    margin = margin_per_category[category]
    start_y, end_y = get_y_boarder(datapoints, margin)

    return render_template("index.html", categories=categories, label=category_label,
                           date_labels=date_labels, datapoints=datapoints, start_y=start_y, end_y=end_y)


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


# stats
@app.route("/stats/all")
def show_all():
    if auth_user not in session:
        return redirect("/login")

    stats = get_stats(session[auth_user])
    beautified_stats = beautify_stats(stats)
    return render_template("index.html", headers=headers, stats=beautified_stats)


@app.route("/stats/add", methods=["GET", "POST"])
def add_entry():
    if request.method == "GET":
        return render_template("add.html")

    if auth_user not in session:
        return redirect("/login")

    ok, err = check_submission(request)
    if not ok:
        return render_template("add.html", error=err)

    date, weight, body_fat, water, muscles = parse_submission(request)
    add_stats(session[auth_user], date, weight, body_fat, water, muscles)
    return redirect("/")


@app.route("/stats/edit", methods=["GET", "POST"])
def edit_entry():
    if auth_user not in session:
        return redirect("/login")

    ok, err = check_submission(request)  # TODO, frontend
    if not ok:
        return render_template("add.html", error=err)  # TODO, frontend

    date, weight, body_fat, water, muscles = parse_submission(request)
    edit_stats(session[auth_user], date, weight, body_fat, water, muscles)
    return render_template("index.html")  # TODO, frontend


@app.route("/stats/del", methods=["GET", "POST"])
def edit_entry():
    if auth_user not in session:
        return redirect("/login")
    date = request.form.get("date")  # TODO, frontend
    if not date:
        return render_template("add.html", error="Date cannot be null")  # TODO, frontend
    delete_stats(session[auth_user], date)
    return 200


"""
@app.route("/delete_user", methods=["GET", "POST"])  # TODO, frontend
def edit_entry():
    if auth_user not in session:
        return redirect("/login")
    delete_user(session[auth_user])
    return render_template("index.html")  # TODO, frontend
"""
