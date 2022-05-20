import json
import pathlib
import sqlite3
from .paper import Paper

SQLITE_FILE = "paper.db"
MAX_SUPPORT_DB_VERSION = 2


# Currently, we are using sqlite3 for storing all data. This makes get() and update_paper() fast.
class Db:
    @staticmethod
    def create(path: pathlib.Path):
        p = path.joinpath(SQLITE_FILE)
        conn = sqlite3.connect(p)
        # TODO: handle error if connect fails
        c = conn.cursor()
        # SQL queries for version 1.
        c.execute("CREATE TABLE papers (idx integer primary key, json text)")
        # SQL queries for version 2.
        Db.version_2_commands(conn, c)
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.filename())

    @staticmethod
    def version_2_commands(conn, c):
        c.execute("CREATE TABLE config (version text)")
        data = (2,)
        c.execute("INSERT INTO config (version) values (?)", data)
        conn.commit()

    @staticmethod
    def upgrade_from_1(conn, c):
        Db.version_2_commands(conn, c)

    @staticmethod
    def upgrade_from_2(conn, c):
        Db.version_3_commands(conn, c)

    def upgrade(self):
        # Version 1: does not has a table config.
        # Version 2: has a table config with a column config which has value 2.
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute("SELECT version FROM config")
            # Nothing to do as the database already has a table to store the config.
        except sqlite3.OperationalError:
            # Upgrade database to version 2.
            Db.upgrade_from_1(conn, c)
        conn.close()

    def __init__(self, path: pathlib.Path, repo):
        self._repo = repo
        self.path = path

    @staticmethod
    def get_version(c):
        return int(c.execute("SELECT version FROM config").fetchone()[0])

    def check_version(self):
        self.upgrade()
        conn = self.get_connection()
        c = conn.cursor()
        v = Db.get_version(c)
        conn.close()
        return v <= MAX_SUPPORT_DB_VERSION

    def filename(self):
        return self.path.joinpath(SQLITE_FILE)

    def list(self):
        conn = self.get_connection()
        c = conn.cursor()
        r = [Paper.from_json(idx, json_data, self._repo) for idx, json_data in sorted([i for i in c.execute("SELECT idx, json FROM papers")])]
        conn.close()
        return r

    def next_id(self):
        conn = self.get_connection()
        c = conn.cursor()
        r = [i[0] for i in c.execute("SELECT idx FROM papers")]
        conn.close()
        if len(r) == 0:
            return 1
        return max(r) + 1

    def add_paper(self, p: Paper):
        conn = self.get_connection()
        c = conn.cursor()
        data = (p.idx(), p.as_json())
        c.execute("INSERT INTO papers (idx, json) VALUES (?, ?)", data)
        conn.commit()
        conn.close()

    def get(self, idx):
        conn = self.get_connection()
        c = conn.cursor()
        r = c.execute("SELECT json FROM papers WHERE idx=" + str(idx))
        r = r.fetchone()
        conn.close()
        if not r:
            return None
        return Paper.from_json(idx, r[0], self._repo)

    def update_paper(self, p: Paper):
        conn = self.get_connection()
        c = conn.cursor()
        data = (p.as_json(), p.idx())
        c.execute("UPDATE papers SET json = ? WHERE idx = ?", data)
        conn.commit()
        conn.close()

