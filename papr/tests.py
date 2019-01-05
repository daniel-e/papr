#!/usr/bin/env python3

import os
import unittest
from pathlib import Path
from lib.config import Config
import shutil


def get_config_path():
    return str(Path.home()) + "/.papr"


def get_config_file():
    return str(Path.home()) + "/.papr/papr.cfg"


def create_default_config():
    shutil.rmtree(get_config_path())
    Config()


class TestConfig(unittest.TestCase):

    # ------- HELP FUNCTIONS ----------------------------------------


    # --------- TESTS -----------------------------------------------

    def test_config_does_not_exist(self):
        """
        Pre: ~/.papr and ~/.papr/papr.cfg does not exist.
        Check:
        - configuratino file ~/papr/papr.cfg should exist
        - default reposiroty = "null"
        - cfg_version = "0.0.1"
        :return:
        """
        p = get_config_path()
        f = get_config_file()

        self.assertFalse(os.path.exists(p))

        c = Config()
        self.assertEqual(c.get("cfg_version"), "0.0.1")
        self.assertEqual(c.get("default_repo"), "null")
        self.assertTrue(os.path.exists(p))
        self.assertTrue(os.path.exists(f))

    def test_config_exists(self):
        """
        Pre: ~/.papr/papr.cfg exists
        Check:
        :return:
        """
        create_default_config()
        self.assertTrue(os.path.exists(get_config_file()))
        c = Config()
        self.assertEqual(c.get("cfg_version"), "0.0.1")
        self.assertEqual(c.get("default_repo"), "null")


if __name__ == "__main__":
    unittest.main()
