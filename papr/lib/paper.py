import json


class Paper:
    def __init__(self, idx, filename, title, tags=[]):
        self._idx = idx
        self._filename = filename
        self._title = title
        self._msg = ""
        self._tags = tags
        self._stars = 0

    @staticmethod
    def from_json(idx, jsonstr):
        p = Paper(idx, filename=None, title=None)
        p._idx = idx
        data = json.loads(jsonstr)
        p._filename = data["filename"]
        p._title = data["title"]
        p._msg = data.get("msg", "")
        p._tags = [i for i in data.get("tags", "").split(",") if len(i) > 0]
        p._stars = int(data.get("stars", "0"))
        return p

    def as_json(self):
        d = {
            "filename": self._filename,
            "title": self._title,
            "msg": self._msg,
            "tags": ",".join(self._tags),
            "stars": self._stars
        }
        return json.dumps(d)

    def remove_tag(self, tag):
        self._tags = [i for i in self._tags if i != tag]

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

    def tags(self):
        return sorted(self._tags)

    def set_tags(self, tags):
        self._tags = tags

    def stars(self):
        return self._stars

    def set_stars(self, n):
        self._stars = max(0, min(5, n))
