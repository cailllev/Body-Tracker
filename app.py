from flask import Flask, redirect, render_template, request, session
from secrets import token_bytes

from db import category_info, categories, beautified_categories, category_to_beautified, default_category, \
    db_init, db_login, db_register, delete_user, get_stats, add_stats, edit_stats, delete_stats, get_route_names, \
    get_routes, add_route, edit_route, delete_route, get_activities, add_activity, edit_activity, delete_activity
from utils import check_stats_submission, parse_stats_submission, check_routes_submission, parse_route_submission, \
    check_activity_submission, parse_activity_submission, beautify_stats, beautify_routes, beautify_activities, \
    parse_stats_for_category, get_y_boarder, stats_headers, routes_headers, activities_headers, margin_per_category

app = Flask(__name__)
app.secret_key = token_bytes(16)
auth_user = "user"

db_init()


@app.route("/")
def index():
    return render_template("index.html")


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


@app.route("/delete", methods=["GET", "POST"])
def delete_my_user():
    if auth_user not in session:
        return redirect("/login")
    if request.method == "GET":
        return render_template("delete_user.html")
    delete_user(session[auth_user])
    return render_template("index.html")


# stats
@app.route("/stats", defaults={"category": ""})
@app.route("/stats/<category>")
def stats_overview(category):
    if auth_user not in session:
        return redirect("/login")

    if category == "" or category not in categories:
        category = default_category
    category_label = category_to_beautified[category]

    stats = get_stats(session[auth_user], category)
    round_to = 1  # round all datapoints to 1 decimal
    datapoints, date_labels = parse_stats_for_category(stats, round_to)

    if datapoints:
        margin = margin_per_category[category]
        start_y, end_y = get_y_boarder(datapoints, margin)
    else:
        start_y, end_y = 0, 100

    return render_template("stats.html", category_info=category_info, selected_category=category, label=category_label,
                           date_labels=date_labels, datapoints=datapoints, start_y=start_y, end_y=end_y)


@app.route("/stats/all")
def stats_show_all():
    if auth_user not in session:
        return redirect("/login")

    stats = get_stats(session[auth_user])
    beautified_stats = beautify_stats(stats)
    return render_template("all_stats.html", categories=beautified_categories, headers=stats_headers,
                           stats=beautified_stats)


@app.route("/stats/add", methods=["GET", "POST"])
def stats_add_entry():
    if auth_user not in session:
        return redirect("/login")

    if request.method == "GET":
        return render_template("add_stats.html")

    ok, err = check_stats_submission(request)
    if not ok:
        return render_template("add_stats.html", error=err)

    date, weight, body_fat, water, muscles = parse_stats_submission(request)
    add_stats(session[auth_user], date, weight, body_fat, water, muscles)
    return redirect("/stats")


"""
@app.route("/stats/edit", methods=["GET", "POST"])
def stats_edit_entry():
    if auth_user not in session:
        return redirect("/login")

    ok, err = check_stats_submission(request)  # TODO, frontend
    if not ok:
        return render_template("add_stats.html", error=err)  # TODO, frontend

    date, weight, body_fat, water, muscles = parse_stats_submission(request)
    edit_stats(session[auth_user], date, weight, body_fat, water, muscles)
    return render_template("stats.html")  # TODO, frontend


@app.route("/stats/del", methods=["GET", "POST"])
def stats_del_entry():
    if auth_user not in session:
        return redirect("/login")
    date = request.form.get("date")  # TODO, frontend
    if not date:
        return render_template("add_stats.html", error="Date cannot be null")  # TODO, frontend
    delete_stats(session[auth_user], date)
    return 200
"""


# routes, TODO
@app.route("/routes")
def routes_overview():
    if auth_user not in session:
        return redirect("/login")

    routes = get_routes(session[auth_user])
    routes = beautify_routes(routes)
    return render_template("routes.html", headers=routes_headers, routes=routes)


@app.route("/routes/add", methods=["GET", "POST"])
def routes_add_entry():
    if auth_user not in session:
        return redirect("/login")

    if request.method == "GET":
        return render_template("add_route.html")

    ok, err = check_routes_submission(request)
    if not ok:
        return render_template("add_routes.html", error=err)

    route_name, distance, height = parse_route_submission(request)
    add_route(session[auth_user], route_name, distance, height)
    return redirect("/routes")


# activities, TODO
@app.route("/activities", defaults={"route": ""})
@app.route("/activities/<route>")
def activities_overview(route):
    if auth_user not in session:
        return redirect("/login")

    if route == "All Routes":
        route = ""
    if route == "":
        selected_route = "All Routes"
    else:
        selected_route = route

    activities = get_activities(session[auth_user], route)
    activities = beautify_activities(activities)
    route_names = get_route_names(session[auth_user])
    route_names.insert(0, "All Routes")
    return render_template("activities.html", selected_route=selected_route, route_names=route_names,
                           headers=activities_headers, activities=activities)


@app.route("/activities/add", methods=["GET", "POST"])
def activities_add_entry():
    if auth_user not in session:
        return redirect("/login")

    if request.method == "GET":
        routes = get_route_names(session[auth_user])
        if not routes:
            return render_template("add_route.html", error="Add a Route first")
        return render_template("add_activity.html", routes=routes)

    ok, err = check_activity_submission(request)
    if not ok:
        return render_template("add_activity.html", error=err)

    date, route_name, time, pace, speed, heart_rate = parse_activity_submission(request, session[auth_user])
    add_activity(session[auth_user], route_name, date, time, pace, speed, heart_rate)
    return redirect(f"/activities/{route_name}")


# debug
if __name__ == "__main__":
    app.run("127.0.0.1", 8811)
