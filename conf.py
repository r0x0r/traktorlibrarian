__author__ = 'roman'

import json
import logging

class Conf(dict):
    pass

conf = Conf()
conf.verbose = logging.DEBUG
conf.is_console = True
conf.filelog = False
