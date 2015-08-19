__author__ = 'roman'

import sys
import os
import operator
import logging
from logger import configure_logger


class Cleaner:

    def __init__(self, library):
        self.library = library
        self._total = len(library.collection)
        self._duplicates = 0
        self._playlist_entries = {}
        self._removed_duplicates = []
        self.logger = configure_logger(logging.getLogger(__name__))

    def remove_duplicates(self):
        """
        Scan library for duplicate entries and deletes them. Duplicates are detected using AUDIO ID information
        stored in the library file
        :return:
        """
        ids = {}
        self.logger.info("\n")

        collection = self.library.collection

        for entry in collection:
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
                new_path = self.library.get_full_path(entry_keep, sys.platform == "win32")

                for entry in remove_entries:
                    old_path = self.library.get_full_path(entry, sys.platform == "win32")
                    self.logger.info(u"Removing \"{}\" in favour of \"{}\"".format(old_path, new_path))
                    self._removed_duplicates.append((old_path, new_path)) # store the same information for UI

                    collection.remove(entry) # remove from the collection
                    self._add_playlist_entry(entry, entry_keep) # save to the playlist dictionary for further processing

                self._duplicates += len(remove_entries)

            elif entry_keep is None:
                artist = remove_entries[0].get("ARTIST")
                title = remove_entries[0].get("TITLE")

                self.logger.info(u"Duplicates of \"{} - {}\" not removed, because none of the source files exist"
                                 .format(artist, title))

        # And now get down to processing playlists
        self.process_playlists()
        collection.set("ENTRIES", str(len(collection)))

    def get_result(self):
        """
        Return result of duplicates removal in form of a dictionary {"count": number_of_duplicates,
        "duplicates": a list of tuples of removed duplicates (old_path, new_path)). Invoked by UI to get information
        about the run.
        :return:
        """

        return {"count": self._duplicates, "duplicates": self._removed_duplicates}

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
            path = self.library.get_full_path(entry, True)

            if sys.platform == "darwin":
                path = os.path.join("/Volumes", path)

            if os.path.exists(path):
                exist_entries.append(entry)

        if not exist_entries:
            return (None, entries)

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
        old_path = self.library.get_full_path(old_entry, True, True)

        if old_path not in self._playlist_entries:
            self._playlist_entries[old_path] = new_entry


    def process_playlists(self):
        """
        Go through playlists and replace removed paths with correct ones
        :return:
        """
        playlists = self.library.playlists

        for playlist_entry in playlists.iter("PRIMARYKEY"):
            path = playlist_entry.get("KEY")
            if path in self._playlist_entries:
                new_entry = self._playlist_entries[path]
                new_path = self.library.get_full_path(new_entry, True, True)
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



