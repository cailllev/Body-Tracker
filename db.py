from hashlib import pbkdf2_hmac
from secrets import token_bytes
from sqlite3 import connect

DB = "db.sqlite"
categories = ["weight", "body_fat", "water", "muscles"]


def init():
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
        cur.execute("INSERT INTO user(username, hashed_pw, salt) "
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


def get_stats(username, cat=""):
    if not cat or cat not in categories:
        select = "SELECT date, weight, body_fat, water, muscles"
    else:
        select = "SELECT date, " + cat
    with connect(DB) as con:
        cur = con.cursor()
        return cur.execute(select + " FROM stats WHERE username = (?) ORDER BY date", (username,)).fetchall()


def add_stats(username, date, weight, body_fat, water, muscles):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO stats(username, date, weight, body_fat, water, muscles) "
                    "VALUES (?, ?, ?, ?, ?, ?)", (username, date, weight, body_fat, water, muscles))
        con.commit()


def edit_stats(username, date, weight, body_fat, water, muscles):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("UPDATE stats WHERE username = (?) AND date = (?) "
                    "SET weight = (?), body_fat = (?), water = (?), muscles = (?)"
                    , (username, date, weight, body_fat, water, muscles))
        con.commit()


def delete_stats(username, date):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM stats WHERE username = (?) and date = (?)", (username, date))
        cur.commit()
