import xml.etree.ElementTree as etree
import shutil
import os
import sys
import copy
import logger

from datetime import datetime
from conf import *


class Library:

    def __init__(self, path):
        self.traktor_path = path
        self.library_path = os.path.join(path, "collection.nml")
        self.tree = etree.parse(self.library_path, parser=etree.XMLParser(encoding="utf-8"))
        self.collection = self.tree.getroot().find("COLLECTION")
        self.playlists = self.tree.getroot().find("PLAYLISTS")

    def flush(self, path=None):
        """
        Write collection XML file to the disk performing a backup of the existing collection first
        :return:
        """
        if path is None:
            self._backup()
            path = self.library_path

        self.tree.write(path, encoding="utf-8", xml_declaration=True)

    def create_new(self):
        version = self.tree.getroot().attrib["VERSION"]
        root = etree.Element("NML", attrib={"VERSION": version})

        etree.SubElement(root, "MUSICFOLDERS")
        etree.SubElement(root, "COLLECTION")
        etree.SubElement(root, "PLAYLISTS")

        return etree.ElementTree(root)

    @staticmethod
    def create_playlist_structure(tree, name, total):
        playlists = tree.getroot().find("PLAYLISTS")
        playlists.clear()

        parent = etree.SubElement(playlists, "NODE", attrib={"TYPE": "FOLDER", "NAME": "$ROOT"})
        parent = etree.SubElement(parent, "SUBNODES", attrib={"COUNT": "1"})
        parent = etree.SubElement(parent, "NODE", attrib={"TYPE": "PLAYLIST", "NAME": name})
        return etree.SubElement(parent, "PLAYLIST", attrib={"ENTRIES": str(total), "TYPE": "LIST", "UUID": ""})

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
            full_path = self.traktorize_path(full_path)

        if include_volume:
            volume = location.get("VOLUME")
            full_path = volume + full_path  # we cannot use os.path.join as the path is in the absolute form already

        return full_path

    def traktorize_path(self, path):
        """
        Convert a path to the Traktor format, that is with a colon preceding each directory name
        :param path: Path to convert
        :return: Traktorized path
        """

        # / is a valid filename character on OSX, so we must escape it before splitting the path
        path = path.replace("//", "%___%")
        path_parts = path.split("/")
        separator = "/:"

        return separator.join(path_parts).replace("%___%", "//")
