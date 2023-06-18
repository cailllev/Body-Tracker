from hashlib import pbkdf2_hmac
from secrets import token_bytes
from sqlite3 import connect
from string import ascii_letters, digits

DB = "db.sqlite"
categories = ["weight", "body_fat", "water", "muscles"]


def check_save_query_input(q):
    if any(c not in ascii_letters + digits + "-_" for c in q):
        return False  # 1337 h4xor detected
    return True


def db_init():
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS user ("
                    "username TEXT PRIMARY KEY,"
                    "hashed_pw TEXT,"
                    "salt TEXT"
                    ")")
        cur.execute("CREATE TABLE IF NOT EXISTS stats ("
                    "username TEXT,"
                    "date INT,"      # epoch timestamp
                    "weight NUM,"    # kilos
                    "body_fat NUM,"  # percents
                    "water NUM,"     # percents
                    "muscles NUM,"   # percents
                    "PRIMARY KEY (username, date),"
                    "FOREIGN KEY (username) REFERENCES user (username) ON DELETE CASCADE"
                    ")")
        cur.execute("CREATE TABLE IF NOT EXISTS routes ("
                    "username TEXT,"
                    "route_name TEXT,"
                    "distance INT,"  # meters
                    "height INT,"    # meters
                    "PRIMARY KEY (username, route_name),"
                    "FOREIGN KEY (username) REFERENCES user (username) ON DELETE CASCADE"
                    ")")
        cur.execute("CREATE TABLE IF NOT EXISTS activities ("
                    "username TEXT,"
                    "route_name TEXT,"
                    "date INT,"        # epoch timestamp
                    "time INT,"        # seconds
                    "pace NUM,"        # min/km
                    "speed NUM,"       # km/h
                    "heart_rate INT,"  # bpm
                    "PRIMARY KEY (username, route_name, date),"
                    "FOREIGN KEY (username) REFERENCES user (username) ON DELETE CASCADE"
                    ")")
        con.commit()


def h(password: str, salt: str) -> str:
    return pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 2**18).hex()


def db_register(username, password):
    salt = token_bytes(16).hex()
    hashed_pw = h(password, salt)
    with connect(DB) as con:
        cur = con.cursor()
        if cur.execute("SELECT * FROM user WHERE username = (?)", (username,)).fetchall():
            return False
        cur.execute("INSERT INTO user (username, hashed_pw, salt) "
                    "VALUES (?, ?, ?)", (username, hashed_pw, salt))
        con.commit()
        return True


def delete_user(username):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM user WHERE username = (?)", (username,))


def db_login(username, given_password):
    with connect(DB) as con:
        cur = con.cursor()
        if ret := cur.execute("SELECT * FROM user WHERE username = (?)", (username,)).fetchone():
            username, hashed_pw, salt = ret
            return h(given_password, salt) == hashed_pw


def get_stats(username, category=""):
    if not category:
        select = "SELECT date, weight, body_fat, water, muscles"
    elif category not in categories or not check_save_query_input(category):
        return []
    else:
        select = "SELECT date, " + category
    with connect(DB) as con:
        cur = con.cursor()
        return cur.execute(select + " FROM stats WHERE username = (?) ORDER BY date", (username,)).fetchall()


def add_stats(username, date, weight, body_fat, water, muscles):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO stats (username, date, weight, body_fat, water, muscles) "
                    "VALUES (?, ?, ?, ?, ?, ?)", (username, date, weight, body_fat, water, muscles))
        con.commit()


def edit_stats(username, date, weight, body_fat, water, muscles):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("UPDATE stats WHERE username = (?) AND date = (?) "
                    "SET weight = (?), body_fat = (?), water = (?), muscles = (?)",
                    (username, date, weight, body_fat, water, muscles))
        con.commit()


def delete_stats(username, date):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM stats WHERE username = (?) and date = (?)", (username, date))
        con.commit()


def get_route_names(username):
    with connect(DB) as con:
        cur = con.cursor()
        routes = cur.execute("SELECT route_name FROM routes WHERE username = (?)", (username,)).fetchall()
        routes = [r[0] for r in routes]  # routes are [("route1",),("route2"),...]
        return routes


def get_routes(username, route_name=""):
    if not check_save_query_input(route_name):
        return []
    if route_name:
        add_query = f'AND route_name = "{route_name}" '
    else:
        add_query = "ORDER BY route_name"
    with connect(DB) as con:
        cur = con.cursor()
        return cur.execute("SELECT route_name, distance, height FROM routes WHERE username = (?) " + add_query,
                           (username,)).fetchall()


def get_route_details(username, route_name):
    with connect(DB) as con:
        cur = con.cursor()
        return cur.execute("SELECT distance, height FROM routes WHERE username = (?) AND route_name = (?)",
                           (username, route_name)).fetchone()


def add_route(username, route_name, distance, height):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO routes (username, route_name, distance, height) VALUES (?, ?, ?, ?)",
                    (username, route_name, distance, height))
        con.commit()


def edit_route(username, route_name, distance, height):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("UPDATE routes WHERE username = (?) AND route_name = (?) SET distance = (?), height = (?)",
                    (username, route_name, distance, height))
        con.commit()


def delete_route(username, route_name):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM routes WHERE username = (?) and route_name = (?)", (username, route_name))
        con.commit()


def get_activities(username, route_name=""):
    if not check_save_query_input(route_name):
        return []
    if route_name:
        add_query = f'AND route_name = "{route_name}" ORDER by date'
    else:
        add_query = "ORDER BY route_name, date"
    with connect(DB) as con:
        cur = con.cursor()
        return cur.execute("SELECT route_name, date, time, pace, speed, heart_rate FROM activities "
                           "WHERE username = (?) " + add_query, (username,)).fetchall()


def add_activity(username, route_name, date, time, pace, speed, heart_rate):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO activities (username, route_name, date, time, pace, speed, heart_rate) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)", (username, route_name, date, time, pace, speed, heart_rate))
        con.commit()


def edit_activity(username, route_name, date, time, pace, speed, heart_rate):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("UPDATE activities WHERE username = (?) AND route_name = (?) AND date = (?) "
                    "SET time = (?), pace = (?), speed = (?), heart_rate = (?)",
                    (username, route_name, date, time, pace, speed, heart_rate))
        con.commit()


def delete_activity(username, route_name, date):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM activities WHERE username = (?) AND route_name = (?) AND date = (?)",
                    (username, route_name, date))
        con.commit()
