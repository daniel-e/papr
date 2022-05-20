import json


class Paper:
    def __init__(self, idx, filename, title, tags=[]):
        self._idx = idx
        self._filename = filename
        self._title = title
        self._msg = ""
        self._tags = tags
        self._stars = 0
        self._url = ""
        self._abstract = ""
        self._hidden = False
        self._summary = ""
        self._highlights = []  # for search

    @staticmethod
    def from_json(idx, jsonstr):
        p = Paper(idx, filename=None, title=None)
        p._idx = idx
        data = json.loads(jsonstr)
        p._filename = data["filename"]
        p._title = data["title"]
        p._msg = data.get("msg", "")          # notes -> only relevant for v1 repositories
        p._summary = data.get("summary", "")  # only relevant for v1 repositories
        p._tags = [i for i in data.get("tags", "").split(",") if len(i) > 0]
        p._stars = int(data.get("stars", "0"))
        p._abstract = data.get("abstract", "")
        p._url = data.get("url", "")
        p._hidden = False if data.get("hidden", "n") == "n" else True
        return p

    def as_nice_dict(self):
        mapping = {
            "filename": "Filename",
            "title": "Title",
            "msg": "Notes",
            "summary": "Summary",
            "tags": "Tags",
            "stars": "Voting",
            "abstract": "Abstract",
            "url": "URL"
        }
        r = {mapping.get(i, "<unknown>"): j for i, j in self._as_dict().items()}
        return r

    def _as_dict(self):
        d = {
            "filename": self._filename,
            "title": self._title,
            "msg": "",  # with repo v2 not stored in sqlite3 db anymore
            "summary": "",  # with repo v2 not stored in sqlite3 db anymore
            "tags": ",".join(self._tags),
            "stars": self._stars,
            "abstract": self._abstract,
            "url": self._url,
            "hidden": "y" if self._hidden else "n"
        }
        return d

    def as_json(self):
        return json.dumps(self._as_dict())

    def remove_tag(self, tag):
        self._tags = [i for i in self._tags if i != tag]

    def idx(self):
        return self._idx

    def filename(self):
        return self._filename

    def title(self):
        return self._title

    def set_title(self, t):
        self._title = t

    def msg(self):  # Notes
        return self._msg

    def update_msg(self, msg):
        self._msg = msg

    def summary(self):
        return self._summary

    def update_summary(self, summary):
        self._summary = summary

    def has_notes(self):
        return len(self._msg) > 0

    def has_summary(self):
        return len(self.summary()) > 0

    def tags(self):
        """
        Returns a list of tags.
        :return:
        """
        return sorted(self._tags)

    def set_tags(self, tags):
        self._tags = tags

    def stars(self):
        return self._stars

    def set_stars(self, n):
        self._stars = max(0, min(5, n))

    def set_abstract(self, abstract):
        self._abstract = ""
        if abstract is not None:
            self._abstract = abstract

    def set_url(self, url):
        self._url = url

    def abstract(self):
        return self._abstract

    def url(self):
        return self._url

    def set_highlights(self, positions):
        self._highlights = positions

    def highlights(self):
        return self._highlights

    def hidden(self):
        return self._hidden

    def hide(self, value=True):
        self._hidden = value
