__author__ = 'roman'

import json
import logging

CONF_FILE = "conf.json"

class Conf(dict):
    pass

conf = Conf()
conf["verbose"] = logging.ERROR


def load_conf(conf_file):
    loaded_conf = json.load(open(conf_file, 'r'))

    for k, v in loaded_conf.items():
        conf[k] = v

