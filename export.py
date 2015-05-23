import os
import sys
import shutil
import xml.etree.ElementTree as etree
import logging

from Queue import Queue
from threading import Thread

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_logger = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_logger)


class Exporter:
    REPLACE_CHARS = "\/:*?\"<>|"
    MUSIC_DIR = ".Music"

    def __init__(self, library, volume):
        self.library = library
        self.volume = volume
        self.destination = os.path.join("/Volumes", volume)
        self.music_dir = os.path.join(self.destination, Exporter.MUSIC_DIR)

        self.queue = Queue(maxsize=0)
        self._entries = {}

        self._check_volume()

    def export(self):
        tree = self.library.tree
        collection = tree.getroot().find("COLLECTION")
        self._start_copy_thread()

        for entry in collection:
            file_name = entry.find("LOCATION").attrib["FILE"]
            self._entries[file_name] = entry
            self.queue.put(entry)

            location = entry.find("LOCATION")
            location.attrib["DIR"] = "/:" + Exporter.MUSIC_DIR + "/:"
            location.attrib["VOLUME"] = self.volume
            location.attrib["VOLUMEID"] = self.volume

        self._process_playlists()

    def _check_volume(self):
        if not os.path.exists(self.destination):
            raise IOError("Volume {0} does not exist.".format(self.volume))

    def _remove_orphan_files(self, file_paths):
        orphans = set(os.listdir(self.music_dir)) - set(file_paths)
        for orphan in orphans:
            print("Removing {}".format)
            os.remove(orphan)

    def _create_playlist_structure(self, tree, name, total):
        playlists = tree.getroot().find("PLAYLISTS")
        playlists.clear()

        parent = etree.SubElement(playlists, "NODE", attrib={"TYPE": "FOLDER", "NAME": "$ROOT"})
        parent = etree.SubElement(parent, "SUBNODES", attrib={"COUNT": "1"})
        parent = etree.SubElement(parent, "NODE", attrib={"TYPE": "PLAYLIST", "NAME": name})
        return etree.SubElement(parent, "PLAYLIST", attrib={"ENTRIES": str(total), "TYPE": "LIST", "UUID": ""})

    def _create_playlist_entry(self, parent, entry):
        path = self.library.get_full_path(entry, True, True)

        parent = etree.SubElement(parent, "ENTRY")
        etree.SubElement(parent, "PRIMARYKEY", attrib={"KEY": path, "TYPE": "TRACK"})

    def _process_playlists(self):
        def recursive_scan(nodes, directory):
            for node in nodes:
                if node.attrib["TYPE"] == "FOLDER":
                    dir_name = self._replace_filename_char(node.attrib["NAME"])
                    new_dir = os.path.join(directory, dir_name)

                    try:
                        os.mkdir(new_dir)
                    except OSError as e:
                        logger.debug(e)

                    recursive_scan(node.find("SUBNODES"), new_dir)

                elif node.attrib["TYPE"] == "PLAYLIST":
                    name = node.attrib["NAME"]
                    if name == "_LOOPS" or name == "_RECORDINGS":
                        continue
                    if name == "ALL":
                        name = "All Tracks"

                    entries = self._get_playlist_entries(node)
                    self._export_playlist(entries, name, directory)

        nodes = self.library.playlists.find("NODE").find("SUBNODES")
        recursive_scan(nodes, self.destination)

    @staticmethod
    def _replace_filename_char(value):
        for c in Exporter.REPLACE_CHARS:
            value = value.replace(c, '-')
        return value

    def _get_playlist_entries(self, node):
        entries = []

        for playlist_entry in node.find("PLAYLIST"):
            key = playlist_entry.find("PRIMARYKEY")
            file_name = key.attrib["KEY"].split("/:")[-1]

            entries.append(self._entries[file_name])

        return entries

    def _export_playlist(self, entries, name, directory):
        logger.info(u"Exporting playlist {0} to directory {1}".format(name, directory))

        tree = self.library.create_new()
        collection = tree.getroot().find("COLLECTION")
        collection.attrib["ENTRIES"] = str(len(entries))
        playlist = self._create_playlist_structure(tree, name, len(entries))

        for entry in entries:
            collection.append(entry)
            self._create_playlist_entry(playlist, entry)

        name = self._replace_filename_char(name)
        full_path = os.path.join(directory, name + u".nml")
        tree.write(full_path, encoding="utf-8", xml_declaration=True)

    def _start_copy_thread(self):
        worker = Thread(target=self._copy_files, args=(self.queue,))
        #worker.setDaemon(True)
        worker.start()

    def _copy_files(self, file_paths):
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)

        while not self.queue.empty():
            entry = self.queue.get()

            location = entry.find("LOCATION")
            src_path = os.path.join(location.attrib["DIR"].replace("/:", "/"), location.attrib["FILE"])
            file_name = location.attrib["FILE"]

            try:
                if os.path.exists(src_path) and not os.path.exists(os.path.join(self.music_dir, file_name)):
                    destination_path = os.path.join(self.music_dir, file_name)
                    print (u"Copying {}".format(file_name))
                    self._copy(src_path, destination_path)

            except IOError as e:
                # add logger
                pass

            self.queue.task_done()


def _copy(self, src, dst, buffer_size=10485760):
        '''
        Copies a file to a new location. Much faster performance than Apache Commons due to use of larger buffer
        @param src:    Source File
        @param dst:    Destination File (not file path)
        @param buffer_size:    Buffer size to use during copy
        '''
        #    Check to make sure destination directory exists. If it doesn't create the directory
        try:
            dstParent, dstFileName = os.path.split(dst)
            if(not(os.path.exists(dstParent))):
                os.makedirs(dstParent)

            #    Optimize the buffer for small files
            buffer_size = min(buffer_size, os.path.getsize(src))
            if buffer_size == 0:
                buffer_size = 1024

            if shutil._samefile(src, dst):
                raise shutil.Error("`%s` and `%s` are the same file" % (src, dst))
            for fn in [src, dst]:
                try:
                    st = os.stat(fn)
                except OSError:
                    # File most likely does not exist
                    pass
                else:
                    # XXX What about other special files? (sockets, devices...)
                    if shutil.stat.S_ISFIFO(st.st_mode):
                        raise shutil.SpecialFileError("`%s` is a named pipe" % fn)
            with open(src, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst, buffer_size)

            shutil.copystat(src, dst)

        except OSError:
            pass

