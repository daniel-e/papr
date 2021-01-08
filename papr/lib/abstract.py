import re
import urllib
import urllib.request
from bs4 import BeautifulSoup


def parse_arxiv_abstract(data):
    h = BeautifulSoup(data, "html.parser")
    r = h.find_all("blockquote", {"class": "abstract"})
    if len(r) > 0:
        for i in r[0].find_all("span"):
            i.decompose()
        return r[0].get_text().replace("\n", " ").strip()
    return None


def parse_with_re(data, regx):
    d = data.decode("utf-8", errors="ignore").replace("\n", " ")
    m = regx.match(d)
    if m is not None:
        return m.group(1)
    return None


def parse_openreview_abstract(data):
    c = re.compile(r".*Abstract:</strong>\s*<span[^>]+>(.*?)</span>.*")
    return parse_with_re(data, c)


def parse_neurips_abstract(data):
    c = re.compile(r".*<h4>Abstract</h4>\s*<p>(.*?)</p>.*")
    return parse_with_re(data, c)


def parse_abstract(data):
    r = parse_arxiv_abstract(data)
    if r is None:
        r = parse_openreview_abstract(data)
    if r is None:
        r = parse_neurips_abstract(data)
    return r


def load_abstract(url):
    # TODO merge this with cmd_fetch.py
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    rsp = urllib.request.urlopen(req)
    data = rsp.read()
    data = parse_abstract(data)
    return data


if __name__ == "__main__":
    print("arxiv")
    print(load_abstract("https://arxiv.org/abs/1905.05454"))
    print("openreview")
    print(load_abstract("https://openreview.net/forum?id=HkNDsiC9KQ"))
