import sqlite3
from lib.paper import Paper

SQLITE_FILE = "paper.db"

class Db:
    @staticmethod
    def create(path):
        conn = sqlite3.connect(path + "/" + SQLITE_FILE)
        # TODO: handle error if connect fails
        c = conn.cursor()
        c.execute("CREATE TABLE papers (idx integer primary key, json text)")
        conn.commit()
        conn.close()
        # TODO: handle db errors

    def __init__(self, path):
        self.path = path

    def filename(self):
        return self.path + "/" + SQLITE_FILE

    def list(self):
        conn = sqlite3.connect(self.filename())
        # TODO: handle error if connect fails
        c = conn.cursor()
        r = [Paper.from_json(j[0], j[1]) for j in sorted([i for i in c.execute("SELECT idx, json FROM papers")])]
        conn.close()
        # TODO: handle db errors
        return r
