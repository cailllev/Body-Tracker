from datetime import datetime
from time import time

from db import check_save_query_input, get_route_details

margin_per_category = {"weight": 5, "body_fat": 2, "water": 5, "muscles": 5}
stats_headers = ["Date", "Weight", "% Fat", "% H2O", "% Msl"]
routes_headers = ["Name", "Distance [km]", "Height [m]"]
activities_headers = ["Name", "Date", "Time", "Pace", "Speed"]


def check_stats_submission(request):
    weight = request.form.get("weight")
    body_fat = request.form.get("body_fat")
    water = request.form.get("water")
    muscles = request.form.get("muscles")
    if not all(e for e in [weight, body_fat, water, muscles]):
        return False, "Values cannot be Null"
    try:
        _ = float(weight), float(body_fat), float(water), float(muscles)
    except ValueError:
        return False, "Values must be Numbers"
    return True, ""


def parse_stats_submission(request):
    date = int(time())
    weight = request.form.get("weight")
    body_fat = request.form.get("body_fat")
    water = request.form.get("water")
    muscles = request.form.get("muscles")
    weight, body_fat, water, muscles = float(weight), float(body_fat), float(water), float(muscles)
    return date, weight, body_fat, water, muscles


def check_routes_submission(request):
    route_name = request.form.get("route_name")
    if not route_name:
        return False, "Route Name cannot be Empty"
    if not check_save_query_input(route_name):
        return False, "Route Name can only contain Letters, Numbers and '-_'."
    distance = request.form.get("distance")
    height = request.form.get("height")
    if not all(e for e in [distance, height]):
        return False, "Values cannot be Null"
    try:
        _ = float(distance), float(height)
    except ValueError:
        return False, "Values must be Numbers"
    return True, ""


def parse_route_submission(request):
    route_name = request.form.get("route_name")
    distance = request.form.get("distance")
    height = request.form.get("height")
    distance, height = int(distance), int(height)
    return route_name, distance, height


def check_activity_submission(request):
    route_name = request.form.get("route_name")
    if not check_save_query_input(route_name):
        return False, "Name can only contain Letters, Numbers and '-_'."
    time_min = request.form.get("time_min")
    time_sec = request.form.get("time_sec")
    if not time_min:
        return False, "Time [min] cannot be Null"
    try:
        _ = int(time_min)
        if time_sec is not None:
            _ = int(time_sec)
    except ValueError:
        return False, "Times must be Numbers"
    return True, ""


def parse_activity_submission(request, username):
    date = int(time())
    route_name = request.form.get("route_name")
    time_min = int(request.form.get("time_min"))
    time_sec = int(request.form.get("time_sec"))
    if time_sec is None:
        time_sec = 0
    distance, height = get_route_details(username, route_name)

    total_time_sec = 60*time_min + time_sec
    total_time_min = time_min + time_sec / 60
    total_time_h = time_min / 60 + time_sec / 3600
    total_distance_km = (distance + 10*height) / 1000
    pace = round(total_time_min / total_distance_km, 3)  # min/km
    speed = round(total_distance_km / total_time_h, 3)  # km/h
    return date, route_name, total_time_sec, pace, speed


def parse_date(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%d-%m-%Y')


def parse_stats_for_category(stats, round_to):
    datapoints = []
    date_labels = []
    for row in stats:
        _date, _data_point = row
        date = parse_date(_date)
        datapoint = round(_data_point, round_to)
        datapoints.append(datapoint)
        date_labels.append(date)
    return datapoints, date_labels


def get_y_boarder(datapoints, margin):
    # round(13.3 / 2) * 2 -> round(6.75) * 2 -> 7*2 -> 14 +- 2
    start_y = round(min(datapoints) / margin) * margin - margin
    end_y = round(max(datapoints) / margin) * margin + margin
    return start_y, end_y


def beautify_stats(stats) -> [[str]]:
    beautified_stats = []
    for row in stats:
        _date, _weight, _body_fat, _water, _muscles = row
        date = parse_date(_date)
        weight = "%.1f" % round(_weight, 1) + " kg"
        body_fat = "%.1f" % round(_body_fat, 1) + " %"
        water = "%.1f" % round(_water, 1) + " %"
        muscles = "%.1f" % round(_muscles, 1) + " %"
        beautified_stats.append((date, weight, body_fat, water, muscles))
    return beautified_stats


def beautify_routes(routes) -> [[str]]:
    beautified_routes = []
    for row in routes:
        route_name, _distance, height = row
        distance = "%.1f" % round(_distance / 1000, 1) + " km"
        height = f"{height} m"
        beautified_routes.append((route_name, distance, height))
    return beautified_routes


def beautify_activities(activities) -> [[str]]:
    beautified_activities = []
    for row in activities:
        route_name, _date, _time, _pace, _speed = row
        date = parse_date(_date)
        _time_min, _time_sec = divmod(_time, 60)
        t = f"{_time_min:02}:{_time_sec:02}"  # pad 5:9 to 05:09
        pace = _pace + " min/km"
        speed = "%.1f" % round(_speed, 1) + " km/h"
        beautified_activities.append((route_name, date, t, pace, speed))
    return beautified_activities
