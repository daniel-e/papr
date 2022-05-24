from pathlib import Path
import json
import os


class Config:
    _PAPR_VERSION = "0.0.20"

    def __init__(self):
        self.config_path = str(Path.home()) + "/.papr"
        self.config_file = self.config_path + "/papr.cfg"
        self._read_config()
        self._latest_version = ""

    def get(self, key, default=""):
        return self.config.get(key, default)

    def _read_config(self):
        if not os.path.exists(self.config_path):
            os.mkdir(self.config_path)
        if not os.path.exists(self.config_file):
            self._create_default()
        f = open(self.config_file, "r")
        self.config = json.loads(f.read())
        f.close()

    def _create_default(self):
        self.config = {
            "cfg_version": "0.0.2",
            "default_repo": "null",
            "viewer": "/usr/bin/evince",
            "last_version_started": self.papr_version(),
            "browser": "firefox",
            "browser_params": []
        }
        self._write_config()

    def _write_config(self):
        f = open(self.config_file, "w")
        f.write(json.dumps(self.config))
        f.close()

    def get_export_path(self, default):
        return self.get("export_path", default)

    def set_export_path(self, path):
        self.config["export_path"] = path
        self._write_config()

    def get_viewer(self):
        return self.get("viewer", "/usr/bin/evince")

    def set_viewer(self, path_viewer):
        self.config["viewer"] = path_viewer
        self._write_config()

    def set_default_repo(self, path):
        self.config["default_repo"] = path
        self._write_config()

    def latest_version(self):
        return self._latest_version

    def set_latest_version(self, version):
        self._latest_version = version

    def papr_version(self):
        return self._PAPR_VERSION

    def new_features_already_shown(self):
        key = "last_version_started"
        v = self.papr_version()
        last_version_started = self.config.get(key, "")
        if last_version_started != v:
            self.config[key] = v
            self._write_config()
            return False
        return True

    def get_browser(self):
        return self.get("browser", "firefox")

    def get_browser_params(self):
        return self.get("browser_params", [])

    def set_browser(self, browser):
        self.config["browser"] = browser
        self._write_config()

    def set_browser_params(self, params):
        self.config["browser_params"] = params
        self._write_config()
