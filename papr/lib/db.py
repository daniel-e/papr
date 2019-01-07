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

    def next_id(self):
        conn = sqlite3.connect(self.filename())
        # TODO: handle error if connect fails
        c = conn.cursor()
        r = [i[0] for i in c.execute("SELECT idx FROM papers")]
        conn.close()
        # TODO: handle db errors
        if len(r) == 0:
            return 1
        return max(r) + 1

    def add_paper(self, p: Paper):
        conn = sqlite3.connect(self.filename())
        # TODO: handle error if connect fails
        c = conn.cursor()
        data = (p.idx(), p.as_json())
        c.execute("INSERT INTO papers (idx, json) VALUES (?, ?)", data)
        conn.commit()
        conn.close()
        # TODO: handle db errors

    def get(self, idx):
        conn = sqlite3.connect(self.filename())
        # TODO: handle error if connect fails
        c = conn.cursor()
        r = c.execute("SELECT json FROM papers WHERE idx=" + str(idx))
        r = r.fetchone()
        conn.close()
        # TODO: handle db errors
        if not r:
            return None
        return Paper.from_json(idx, r[0])

    def update_paper(self, p: Paper):
        conn = sqlite3.connect(self.filename())
        # TODO: handle error if connect fails
        c = conn.cursor()
        data = (p.as_json(), p.idx())
        c.execute("UPDATE papers SET json = ? WHERE idx = ?", data)
        conn.commit()
        conn.close()
        # TODO: handle db errors

