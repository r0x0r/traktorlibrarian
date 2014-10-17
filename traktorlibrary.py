__author__ = 'roman'

import sys
import os
import xml.etree.ElementTree as etree
import shutil
import unicodedata
import operator

from datetime import datetime
from conf import *




class Library:

    def __init__(self):
        self._set_logger()
        self.library_path = os.path.join(conf["library_dir"], "collection.nml")
        self.tree = etree.parse(self.library_path)
        self.root = self.tree.getroot()
        self.collection = self.root.find("COLLECTION")
        self._total = len(self.collection)
        self._duplicates = 0
        self._playlist_entries = {}


    def remove_duplicates(self):
        """
        Scan library for duplicate entries and deletes them. Duplicates are detected using AUDIO ID information
        stored in the library file
        :return:
        """
        ids = {}
        self.logger.info("\n")

        for entry in self.collection:
            audio_id = entry.get("AUDIO_ID")
            if audio_id is None:
                continue

            if audio_id not in ids:
                ids[audio_id] = []

            ids[audio_id].append(entry)

        #Discard unique entries
        duplicates = [entries for entries in ids.values() if len(entries) > 1]

        # Remove duplicates
        for dup in duplicates:
            entry_keep, remove_entries = self._choose_entry(dup)

            if remove_entries is not None and entry_keep is not None:
                new_path = self._get_full_path(entry_keep, sys.platform == "win32")

                for entry in remove_entries:
                    old_path = self._get_full_path(entry, sys.platform == "win32")
                    self.logger.info(u"Removing \"{}\" in favour of \"{}\"".format(old_path, new_path))

                    self.collection.remove(entry) # remove from the collection
                    self._add_playlist_entry(entry, entry_keep) # save to the playlist dictionary for further processing

                self._duplicates += len(remove_entries)

        # And now get down to processing playlists
        self.process_playlists()
        self.collection.set("ENTRIES", str(len(self.collection)))


    def _choose_entry(self, entries):
        """
        Check duplicate XML entries in the provided list, decide which one to keep and return one entry to keep and
        entries to delete. The choice
        is made whether on basis which file path exists with the missing path entry discarded. If all the entries do not
        exist, then None is returned. If more than one entry exist on the hard drive, then the choice is made by the
        number of cue points set for the entry.
        :param entries: List of XML entry duplicates
        :return: a tuple of form (entry_to_keep, [entries to delete]). None if all the entries do not exist.
        """

        def getlen_cuepoints(entry):
             return len(entry.findall("CUE_V2"))

        exist_entries = []

        for entry in entries:
            path = self._get_full_path(entry, sys.platform == "win32")

            if os.path.exists(path):
                exist_entries.append(entry)

        if not exist_entries:
            return (None, None)

        # get entry with the most number of cue points
        entry_keep = max([(getlen_cuepoints(e), e) for e in exist_entries], key=operator.itemgetter(0))[1]
        entries.remove(entry_keep)

        return (entry_keep, entries)


    def _add_playlist_entry(self, old_entry, new_entry):
        """
        Adds a new path to the dictionary of playlist entries to replace missing paths.
        :param old_path: Path to the missing file
        :param new_path: Correct path
        :return:
        """
        old_path = self._get_full_path(old_entry, True, True)

        if old_path not in self._playlist_entries:
            self._playlist_entries[old_path] = new_entry


    def process_playlists(self):
        """
        Go through playlists and replace removed paths with correct ones
        :return:
        """
        playlists = self.root.find("PLAYLISTS")

        for playlist_entry in playlists.iter("PRIMARYKEY"):
            path = playlist_entry.get("KEY")
            if path in self._playlist_entries:
                new_entry = self._playlist_entries[path]
                new_path = self._get_full_path(new_entry, True, True)
                playlist_entry.set("KEY", new_path)
                self.logger.debug(u"Playlist entry changed from \"{}\" to \"{}\"".format(path, new_path))

                # Windows version of Traktor uses UUIDs for playlist entries, so those have to be updated as well
                if sys.platform == "win32":
                    uuid = new_entry.get("UUID")
                    playlist_entry.set("UUID", uuid)



    def report(self):
        """
        Print a short report on what was done after the run.
        :return:
        """
        print("\n{} entries processed in total".format(self._total))

        if self._duplicates == 1:
            print("{} duplicate removed".format(self._duplicates))
        else:
            print("{} duplicates removed".format(self._duplicates))



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
