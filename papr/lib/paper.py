import json


class Paper:
    def __init__(self, idx, filename, title):
        self.idx = idx
        self.filename = filename
        self.title = title

    @staticmethod
    def from_json(idx, jsonstr):
        p = Paper(idx, filename=None, title=None)
        p.idx = idx
        data = json.loads(jsonstr)
        p.filename = data["filename"]
        p.title = data["title"]
        return p

    def as_json(self):
        d = {"filename": self.filename, "title": self.title}
        return json.dumps(d)
