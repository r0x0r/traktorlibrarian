import os
import shutil

class Exporter:

    MUSIC_DIR = "Music"

    def __init__(self, library, volume):
        self.library = library
        self.volume = volume
        self.destination = os.path.join("/Volumes", volume)
        self.music_dir = os.path.join(self.destination, Exporter.MUSIC_DIR)

        self._total = len(library.collection)
        self._playlist_entries = {}

        self._check_volume()

    def export(self):
        collection = self.library.collection

        file_paths = []

        for entry in collection:
            location = entry.find("LOCATION")

            full_path = os.path.join(location.attrib["DIR"].replace("/:", "/"), location.attrib["FILE"])
            file_paths.append((full_path, location.attrib["FILE"]))

            location.attrib["DIR"] = "/:" + Exporter.MUSIC_DIR
            location.attrib["VOLUME"] = self.volume

        self._copy(file_paths)
        self.library.flush(os.path.join(self.destination, "collection.nml"))

    def _check_volume(self):
        if not os.path.exists(self.destination):
            raise IOError("Volume {0} does not exist.".format(self.volume))

    def _copy(self, file_paths):
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)

        for full_path, file_name in file_paths:
            try:
                if os.path.exists(full_path) and not os.path.exists(os.path.join(self.music_dir, file_name)):
                    shutil.copyfile(full_path, self.music_dir)

            except IOError as e:
                # add logger
                pass



