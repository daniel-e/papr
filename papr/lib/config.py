from pathlib import Path
import json
import os


class Config:
    def __init__(self):
        self.config_path = str(Path.home()) + "/.papr"
        self.config_file = self.config_path + "/papr.cfg"
        self._read_config()

    def get(self, key):
        return self.config[key]

    def _read_config(self):
        if not os.path.exists(self.config_path):
            os.mkdir(self.config_path)
        if not os.path.exists(self.config_file):
            self._create_default()
        f = open(self.config_file, "r")
        self.config = json.loads(f.read())
        f.close()

    def _create_default(self):
        self.config = {"cfg_version": "0.0.1", "default_repo": "null"}
        self._write_config()

    def _write_config(self):
        f = open(self.config_file, "w")
        f.write(json.dumps(self.config))
        f.close()

    def set_default_repo(self, path):
        self.config["default_repo"] = path
        self._write_config()

