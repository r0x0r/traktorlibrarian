__author__ = 'roman'

import copy
import sys
import os
import math
import xml.etree.ElementTree as etree
import subprocess
import shutil
import unicodedata

from datetime import datetime
from conf import *




class Library:

    DURATION_DELTA = 2    # Maximum difference in track lengths to treat files as identical
    BITRATE_DELTA = 3000  # Maximum difference in bitrates to treat files as identical

    _total = 0
    _duplicates = 0
    _missing_replaced = 0
    _missing_deleted = 0
    _missing_present = 0

    _playlist_entries = {}

    def __init__(self):
        self._set_logger()
        self.library_path = os.path.join(conf["library_dir"], "collection.nml")
        self.tree = etree.parse(self.library_path)
        self.root = self.tree.getroot()
        self.collection = self.root.find("COLLECTION")
        self._total = len(self.collection)


    def remove_duplicates(self):
        """
        Scans library for duplicate entries and deletes them. Duplicates are detected using AUDIO ID information
        stored in the library file
        :return:
        """
        ids = {}

        for entry in self.collection:
            full_path = self._get_full_path(entry)
            audio_id = entry.get("AUDIO_ID")
            if audio_id is None or not os.path.exists(full_path):  # skip if file does not exist
                continue

            if audio_id in ids:
                old_path = self._get_full_path(entry, True, True)
                self._add_playlist_entry(old_path, ids[audio_id]) # save file info for further processing of playlists
                self.remove_entry(entry, full_path, "duplicate")

            else:
                ids[audio_id] = full_path

        self.collection.set("ENTRIES", str(len(self.collection)))


    def fix_missing_files(self):
        """
        Locate or remove missing files depending on which configuration flag is set.
        :return:
        """
        delete_entries = []

        for entry in self.collection:
            full_path = self._get_full_path(entry)

            if not os.path.exists(full_path):
                if conf["fix_missing"]:
                    if not self.replace_missing_entry(entry) and conf["remove_missing"]:
                        # We store entry for later removal in order for them to appear after fixed entries
                        # in the log file
                        delete_entries.append(entry)
                elif conf["remove_missing"]:
                    self.remove_entry(entry, full_path, "missing")

        for entry in delete_entries:
            full_path = self._get_full_path(entry)
            self.remove_entry(entry, full_path, "missing")

        self.collection.set("ENTRIES", str(len(self.collection)))


    def remove_entry(self, entry, full_path, reason):
        """
        Remove an entry from the library. Used both for missing and duplicate entries.
        :param entry: Entry to remove
        :param full_path: Full path of the file
        :param reason: Reason for deletion. Can take either "missing" or "duplicate" value
        :return:
        """
        self.logger.info(u"Removing {} file: {}".format(reason, full_path))
        self.collection.remove(entry)

        if reason == "missing":
            self._missing_deleted += 1
        elif reason == "duplicate":
            self._duplicates += 1


    def replace_missing_entry(self, entry):
        """
        Attempt to find a missing file and if successfull update the XML entry with the correct path.
        :param entry: Entry with the missing file
        :return: True if file was located, False otherwise
        """
        info = entry.find("INFO")
        artist = entry.get("ARTIST")
        title = entry.get("TITLE")

        try:
            if all([artist, title]):
                bitrate = int(info.get("BITRATE"))
                duration = int(info.get("PLAYTIME"))
                artist = self._escape_string(artist)
                title = self._escape_string(title)
                new_path = self._find_file(artist, title, duration, bitrate)

                if new_path:
                    old_path = self._get_full_path(entry, True, True) # we need this for playlists

                    location = entry.find("LOCATION")
                    dir, file_name = os.path.split(new_path)
                    dir = unicodedata.normalize("NFC", self._traktorize_path(dir + os.path.sep))
                    file_name = unicodedata.normalize("NFC", file_name)
                    location.set("DIR", dir)
                    location.set("FILE", file_name)

                    self._missing_replaced += 1
                    self.logger.info(u"Found replacement for \"{} - {}\": {}".format(artist, title, new_path))

                    new_path = self._get_full_path(entry, True, True)
                    self._add_playlist_entry(old_path, new_path)

                    return True
                else:
                    self._missing_present += 1
                    return False

        except TypeError as e:
            self.logger.debug(u"{} - {} [{}, Duration {}]"
                              .format(artist, title, info.get("BITRATE"), info.get("DURATION")))


    def process_playlists(self):
        """
        Go through playlists and replace missing paths with correct ones
        :return:
        """
        playlists = self.root.find("PLAYLISTS")

        for playlist_entry in playlists.iter("PRIMARYKEY"):
            path = playlist_entry.get("KEY")
            if path in self._playlist_entries:
                new_path = self._playlist_entries[path]
                playlist_entry.set("KEY", new_path)
                self.logger.info(u"Changing playlist entry path from {} to {}".format(path, new_path))


    def report(self):
        """
        Print a short report on what was done after the run.
        :return:
        """
        print "\n{} entries processed in total".format(self._total)

        if conf["remove_duplicates"]:
            print "{} duplicates removed".format(self._duplicates)

        if conf["fix_missing"]:
            print "{} missing file replacements found".format(self._missing_replaced)

            if not conf["remove_missing"]:
                print "{} missing files are present in the library".format(self._missing_deleted)

        if conf["remove_missing"]:
            print "{} missing files are deleted".format(self._missing_deleted)


    def flush(self):
        """
        Write collection XML file to the disk performing a backup of the existing collection first
        :return:
        """
        self._backup()
        self.tree.write(self.library_path, encoding="utf-8", xml_declaration=True)


    def _get_full_path(self, entry, include_volume=False, traktorize=False):
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

        return unicode(full_path)


    def _traktorize_path(self, path):
        """
        Convert a path to the Traktor format, that is with a colon preceding each directory name
        :param path: Path to convert
        :return: Traktorized path
        """
        path_parts = path.split(os.path.sep)
        separator = os.path.sep + ":"

        return separator.join(path_parts)


    def _escape_string(self, string):
        """
        Escape a string for correct parsing in mdfind
        :param string: input string
        :return: escaped string
        """
        return unicode(string.strip().replace("\\", "\\\\").replace("\"", "\\\"").replace("'", "\'"))


    def _add_playlist_entry(self, old_path, new_path):
        """
        Adds a new path to the dictionary of files which path has been changed for further processing
        :param old_path: Path to the missing file
        :param new_path: Correct path
        :return:
        """
        if old_path not in self._playlist_entries:
            self._playlist_entries[old_path] = unicodedata.normalize("NFC", new_path)


    def _find_file(self, artist, title, duration, bitrate):
        """
        Find a file using OSX Spotlight search. 
        :param artist:
        :param title:
        :param duration:
        :param bitrate:
        :return:
        """
        # Bitrate information found in the Spotlight database might differ from the information stored in
        # Traktor, that's why we check for a range
        bitrate_ceiling = bitrate + self.BITRATE_DELTA
        bitrate_floor = bitrate - self.BITRATE_DELTA

        # Same goes for track lengths
        duration_ceiling = math.ceil(duration) + self.DURATION_DELTA
        duration_floor = math.floor(duration) - self.DURATION_DELTA

        search_string = u"kMDItemAuthors=\"{}\"c && kMDItemTitle=\"{}\"c && kMDItemDurationSeconds <= {} && " \
                        u"kMDItemDurationSeconds >= {}".format(artist, title, duration_ceiling, duration_floor)

        if bitrate != -1:
            search_string += u" && kMDItemTotalBitRate <= {} && kMDItemTotalBitRate >= {}".format(bitrate_ceiling,
                                                                                                 bitrate_floor)

        filelist = subprocess.check_output(['mdfind', search_string]).rstrip().split("\n")

        for f in filelist:
            if os.path.exists(f):
                return unicode(f, "utf-8")

        return None


    def _backup(self):
        backup_path = os.path.join(conf["library_dir"], "Backup", "Librarian")

        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        source = os.path.join(conf["library_dir"], "collection.nml")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        destination = os.path.join(backup_path, "collection_{}.nml".format(timestamp))
        shutil.copy(source, destination)



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
