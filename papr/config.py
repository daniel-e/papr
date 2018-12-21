from pathlib import Path
import json
import sys
import os


class Config:
    def __init__(self, repo, configfile, homedir):
        self.repo = repo
        self.configfile = configfile
        self.homedir = homedir

    def create_config(self):
        d = {"version": "0.0.1"}
        cfgfile = self.repo + "/" + self.configfile
        f = open(cfgfile, "w")
        f.write(json.dumps(d))
        f.close()

    def _write_config(self, d):
        home = str(Path.home()) + "/" + self.homedir
        n = home + "/" + self.homedir
        f = open(n, "w")
        f.write(json.dumps(d))
        f.close()

    def read_config(self):
        home = str(Path.home()) + "/" + self.homedir
        if not os.path.exists(home):
            os.mkdir(home)
        n = home + "/" + self.homedir
        if not os.path.exists(n):
            d = {"cfg_version": "0.0.1", "default_repo": "null"}
            self._write_config(d)
        f = open(n, "r")
        r = json.loads(f.read())
        f.close()
        return r

    def update_default_repo(self):
        d = self.read_config()
        if not os.path.exists(self.repo):
            print("Not in a repository.", file=sys.stderr)
            sys.exit(1)
        d["default_repo"] = os.getcwd()
        self._write_config(d)
