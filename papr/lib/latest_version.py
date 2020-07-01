import urllib.request
import re
from threading import Thread


def latest_version(callback):
    t = Thread(target=version_getter, args=(callback,))
    t.start()


def version_getter(callback):
    try:
        URL = "https://raw.githubusercontent.com/daniel-e/papr/master/setup.py"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
        }
        req = urllib.request.Request(URL, headers=headers)
        rsp = urllib.request.urlopen(req)
        if rsp.status / 100 == 2:
            data = rsp.read().decode("utf-8", errors="ignore")
            c = re.compile(r"^\s*version=\"([0-9]+\.[0-9]+\.[0-9]+)\",$")
            for i in data.split("\n"):
                m = c.match(i)
                if m is not None:
                    callback(m.group(1))
                    break
    except:
        pass


def __callback(s):
    print(s)


if __name__ == "__main__":
    latest_version(__callback)
