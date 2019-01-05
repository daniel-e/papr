import sqlite3

SQLITE_FILE = "paper.db"


class Db:
    def __init__(self, path):
        conn = sqlite3.connect(path + "/" + SQLITE_FILE)
        # TODO: handle error if connect fails
        c = conn.cursor()
        c.execute("CREATE TABLE papers (idx integer primary key, json text)")
        conn.commit()
        conn.close()
        # TODO: handle db errors
