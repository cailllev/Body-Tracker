from datetime import datetime
from time import time

margin_per_category = {"weight": 5, "body_fat": 2, "water": 5, "muscles": 5}
headers = ["Date", "Weight", "% Body Fat", "% Water", "% Muscles"]


def check_submission(request):
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


def parse_submission(request):
    date = int(time())
    weight = request.form.get("weight")
    body_fat = request.form.get("body_fat")
    water = request.form.get("water")
    muscles = request.form.get("muscles")
    weight, body_fat, water, muscles = float(weight), float(body_fat), float(water), float(muscles)
    return date, weight, body_fat, water, muscles


def parse_date(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%d-%m-%Y')


def parse_stats_for_category(stats, round_to):
    datapoints = []
    for row in stats:
        _date, _data_point = row
        date = parse_date(_date)
        datapoint = round(_data_point, round_to)
        datapoints.append((date, datapoint))
    return datapoints


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
        weight = str(round(_weight, 1)) + " kg"
        body_fat = str(round(_body_fat, 1)) + " %"
        water = str(round(_water, 1)) + " %"
        muscles = str(round(_muscles, 1)) + " %"

        beautified_stats.append((date, weight, body_fat, water, muscles))

    return beautified_stats
