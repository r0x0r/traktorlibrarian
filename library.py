import xml.etree.ElementTree as etree
import shutil
import os
import sys
import logging

from datetime import datetime
from conf import *

class Library:

    def __init__(self, path):
        self._set_logger()
        self.traktor_path = path
        self.library_path = os.path.join(path, "collection.nml")
        self._tree = etree.parse(self.library_path)
        self.collection = self._tree.getroot().find("COLLECTION")
        self.playlists = self._tree.getroot().find("PLAYLISTS")

    def flush(self, path=None):
        """
        Write collection XML file to the disk performing a backup of the existing collection first
        :return:
        """
        if path is None:
            self._backup()
            path = self.library_path

        self._tree.write(path, encoding="utf-8", xml_declaration=True)

    def _backup(self):
        backup_path = os.path.join(self.traktor_path, "Backup", "Librarian")

        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        destination = os.path.join(backup_path, "collection_{}.nml".format(timestamp))
        shutil.copy(self.library_path, destination)


    def get_full_path(self, entry, include_volume=False, traktorize=False):
        """
        Return the full path to a file from the XML entry. If include_volume flag is true, then the path is prepended
        with the volume name (drive letter on Windows), as this information is required in playlist entries.
        :param entry: XML entry to extract a full path from. If traktorize flag is set, then the path is converted to
        the Traktor format with a colon after each path part
        :param include_volume: if True, then the volume name (disk drive) is appended before the path
        :param traktorize if True, then converts path to the Traktor format
        :return: absolute path to a file
        """

        location = entry.find("LOCATION")
        dir = location.get("DIR").replace(":", "")
        file = location.get("FILE")
        full_path = os.path.join(dir, file)

        if traktorize:
            full_path = self._traktorize_path(full_path)

        if include_volume:
            volume = location.get("VOLUME")
            full_path = volume + full_path # we cannot use os.path.join as the path is in the absolute form already

        return full_path


    def _traktorize_path(self, path):
        """
        Convert a path to the Traktor format, that is with a colon preceding each directory name
        :param path: Path to convert
        :return: Traktorized path
        """
        path_parts = path.split("/")
        separator = "/:"

        return separator.join(path_parts)


    def _set_logger(self):
        """
        Set up loggers for this class. There are two loggers in use. StreamLogger prints information on the screen with
        the default level ERROR (INFO if the verbose flag is set). FileLogger logs INFO entries to the report.log file.
        report.log is never purged, but information from new runs is appended to the end of the file.
        :return:
        """
        self.logger = logging.getLogger(__name__)

        stream_logger = logging.StreamHandler(sys.stdout)
        if conf["verbose"]:
            stream_logger.setLevel(logging.INFO)
        else:
            stream_logger.setLevel(logging.ERROR)

        file_logger = logging.FileHandler('report.log')
        file_logger.setLevel(logging.INFO)

        self.logger.addHandler(file_logger)
        self.logger.addHandler(stream_logger)
        self.logger.setLevel(logging.DEBUG)

        self.logger.info("="*80)
        self.logger.info("TraktorLibrarian run on {}"
                         .format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.logger.info("="*80)