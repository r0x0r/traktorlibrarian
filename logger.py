import sys
import os
import logging
from logging.handlers import SysLogHandler
from datetime import datetime

#from config import get_config_dir



is_filelog = True
is_console = True
logging_level = logging.DEBUG

def get_logger(name):
    """
    Set up loggers for this class. There are two loggers in use. StreamLogger prints information on the screen with
    the default level ERROR (INFO if the verbose flag is set). FileLogger logs INFO entries to the report.log file.
    report.log is never purged, but information from new runs is appended to the end of the file.
    :return:
    """
    def _exception_hook(excType, excValue, traceback, logger):
        logger.error("", exc_info=(excType, excValue, traceback))

    logger = logging.getLogger(name)
    sys.excepthook = _exception_hook
    formatter = logging.Formatter('%(asctime)s - %(message)s')

    if is_console:
        stream_logger = logging.StreamHandler(sys.stdout)
        stream_logger.setLevel(logging_level)
        logger.addHandler(stream_logger)
    else:
        syslog_logger = SysLogHandler()
        syslog_logger.setLevel(logging_level)
        syslog_logger.setFormatter(formatter)
        logger.addHandler(syslog_logger)

    if is_filelog:
        file_logger = logging.FileHandler("log.txt") # os.path.join(get_config_dir(),
        file_logger.setLevel(logging_level)
        file_logger.setFormatter(formatter)
        logger.addHandler(file_logger)

    logger.level = logging_level

    return logger
