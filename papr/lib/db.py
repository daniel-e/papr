import sqlite3
from .paper import Paper

SQLITE_FILE = "paper.db"
MAX_SUPPORT_DB_VERSION = 2


class Db:
    @staticmethod
    def create(path):
        conn = sqlite3.connect(path + "/" + SQLITE_FILE)
        # TODO: handle error if connect fails
        c = conn.cursor()
        # SQL queries for version 1.
        c.execute("CREATE TABLE papers (idx integer primary key, json text)")
        # SQL queries for version 2.
        Db.version_2_commands(conn, c)
#        # SQL queries for version 3.
#        Db.version_3_commands(conn, c)
        conn.commit()
        conn.close()
        # TODO: handle db errors

    def get_connection(self):
        return sqlite3.connect(self.filename())

    @staticmethod
    def version_2_commands(conn, c):
        c.execute("CREATE TABLE config (version text)")
        data = (2,)
        c.execute("INSERT INTO config (version) values (?)", data)
        conn.commit()

    @staticmethod
    def version_3_commands(conn, c):
        pass

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
        # At this point we have at least version 2.
#        while True:
#            if Db.get_version(c) == 2:
#                Db.upgrade_from_2(conn, c)
#            else:
#                break
        conn.close()

    def __init__(self, path):
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
        return self.path + "/" + SQLITE_FILE

    def list(self):
        conn = self.get_connection()
        # TODO: handle error if connect fails
        c = conn.cursor()
        r = [Paper.from_json(j[0], j[1]) for j in sorted([i for i in c.execute("SELECT idx, json FROM papers")])]
        conn.close()
        # TODO: handle db errors
        return r

    def next_id(self):
        conn = self.get_connection()
        # TODO: handle error if connect fails
        c = conn.cursor()
        r = [i[0] for i in c.execute("SELECT idx FROM papers")]
        conn.close()
        # TODO: handle db errors
        if len(r) == 0:
            return 1
        return max(r) + 1

    def add_paper(self, p: Paper):
        conn = self.get_connection()
        # TODO: handle error if connect fails
        c = conn.cursor()
        data = (p.idx(), p.as_json())
        c.execute("INSERT INTO papers (idx, json) VALUES (?, ?)", data)
        conn.commit()
        conn.close()
        # TODO: handle db errors

    def get(self, idx):
        conn = self.get_connection()
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
        conn = self.get_connection()
        # TODO: handle error if connect fails
        c = conn.cursor()
        data = (p.as_json(), p.idx())
        c.execute("UPDATE papers SET json = ? WHERE idx = ?", data)
        conn.commit()
        conn.close()
        # TODO: handle db errors

