__author__ = 'roman'
import sys
import logging

from datetime import datetime
from conf import conf


def configure_logger(logger):
    """
    Set up loggers for this class. There are two loggers in use. StreamLogger prints information on the screen with
    the default level ERROR (INFO if the verbose flag is set). FileLogger logs INFO entries to the report.log file.
    report.log is never purged, but information from new runs is appended to the end of the file.
    :return:
    """
    stream_logger = logging.StreamHandler(sys.stdout)
    if conf["verbose"]:
        stream_logger.setLevel(logging.INFO)
    else:
        stream_logger.setLevel(logging.ERROR)

    logger.addHandler(stream_logger)
    logger.setLevel(logging.DEBUG)

    if conf["filelog"]:
        file_logger = logging.FileHandler('report.log')
        file_logger.setLevel(logging.INFO)

        logger.addHandler(file_logger)

        logger.info("="*80)
        logger.info("TraktorLibrarian run on {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        logger.info("="*80)

    return logger