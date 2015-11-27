__author__ = 'roman'
import sys
import logging
from logging.handlers import SysLogHandler

from datetime import datetime
from conf import conf



def configure_logger(logger):
    """
    Set up loggers for this class. There are two loggers in use. StreamLogger prints information on the screen with
    the default level ERROR (INFO if the verbose flag is set). FileLogger logs INFO entries to the report.log file.
    report.log is never purged, but information from new runs is appended to the end of the file.
    :return:
    """
    def _exception_hook(excType, excValue, traceback, logger=logger):
        logger.error("", exc_info=(excType, excValue, traceback))

    if conf.is_console:
        stream_logger = logging.StreamHandler(sys.stdout)
        stream_logger.setLevel(conf.verbose)
        logger.addHandler(stream_logger)
    else:
        syslog_logger = SysLogHandler()
        syslog_logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("Traktor Librarian: [%(name)s]  %(message)s")
        syslog_logger.setFormatter(formatter)

        logger.addHandler(syslog_logger)
        sys.excepthook = _exception_hook

    if conf.filelog:
        file_logger = logging.FileHandler("report.log")
        file_logger.setLevel(logging.INFO)

        logger.addHandler(file_logger)

        logger.info("="*80)
        logger.info("TraktorLibrarian run on {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        logger.info("="*80)

    logger.level = conf.verbose

    return logger
