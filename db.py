from hashlib import pbkdf2_hmac
from secrets import token_bytes
from sqlite3 import connect

DB = "db.sqlite"


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
                    "weight INT,"    # grams
                    "body_fat INT,"  # promille
                    "water INT,"     # promille
                    "muscles INT,"   # promille
                    "PRIMARY KEY (username, date),"
                    "FOREIGN KEY (username) REFERENCES user (username) ON DELETE CASCADE"
                    ")")
        con.commit()


def h(password: str, salt: bytes) -> str:
    return pbkdf2_hmac("sha256", password.encode(), salt, 2**18).hex()


def db_register(username, password):
    salt = token_bytes(16)
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


def get_stats(username):
    with connect(DB) as con:
        cur = con.cursor()
        return cur.execute("SELECT * FROM stats WHERE username = (?) ORDER BY date", (username,)).fetchall()


def add_stats(username, date, weight, body_fat, water, muscle):
    with connect(DB) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO stats (username, date, weight, body_fat, water, muscle)"
                    "(?, ?, ?, ?, ?, ?)", (username, date, weight, body_fat, water, muscle))
        con.commit()
