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

        self._copy_files(file_paths)
        self.library.flush(os.path.join(self.destination, "All Tracks.nml"))

    def _check_volume(self):
        if not os.path.exists(self.destination):
            raise IOError("Volume {0} does not exist.".format(self.volume))

    def _remove_orphan_files(self, file_paths):
        orphans =  set(os.listdir(self.music_dir)) - set(file_paths)
        for orphan in orphans:
            print "Removing {}".format
            os.remove(orphan)

    def _copy_files(self, file_paths):
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)

        for src_path, file_name in file_paths:
            try:
                if os.path.exists(src_path) and not os.path.exists(os.path.join(self.music_dir, file_name)):
                    destination_path = os.path.join(self.music_dir, file_name)
                    print u"Copying {}".format(file_name)
                    self._copy(src_path, destination_path)

            except IOError as e:
                # add logger
                pass

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

