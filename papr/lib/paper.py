import json


class Paper:
    def __init__(self, idx, filename, title):
        self._idx = idx
        self._filename = filename
        self._title = title
        self._msg = ""

    @staticmethod
    def from_json(idx, jsonstr):
        p = Paper(idx, filename=None, title=None)
        p._idx = idx
        data = json.loads(jsonstr)
        p._filename = data["filename"]
        p._title = data["title"]
        p._msg = data.get("msg", "")

        return p

    def as_json(self):
        d = {"filename": self._filename, "title": self._title, "msg": self._msg}
        return json.dumps(d)

    def idx(self):
        return self._idx

    def filename(self):
        return self._filename

    def title(self):
        return self._title

    def msg(self):
        return self._msg

    def update_msg(self, msg):
        self._msg = msg

    def has_notes(self):
        return len(self._msg) > 0
