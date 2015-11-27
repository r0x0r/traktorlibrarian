import os
import sys
import librarian
import psutil
import threading
import logging

from clean import Cleaner
from export import Exporter
from library import Library
from logger import configure_logger
from conf import *

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
import web
import webview

os.environ["SCRIPT_NAME"] = ""
os.environ["REAL_SCRIPT_NAME"] = ""

urls = (
    "/", "Landing",
    "/init", "Initialize",
    "/check/traktor", "CheckTraktor",
    "/export", "Export",
    "/export/scanvolumes", "ExportVolumeScan",
    "/export/status", "ExportStatus",
    "/export/cancel", "ExportCancel",
    "/clean", "Clean",
    "/clean/confirm", "CleanConfirm",
    "/choose/path", "ChoosePath",
)

render = web.template.render('templates/')
logger = configure_logger(logging.getLogger(__name__))


class Landing:
    def GET(self):
        conf.filelog = False  # disable file logging
        conf.debug = True  # disable verbose messages

        traktor_dir = librarian.get_traktor_dir().replace("\\", "\\\\")

        if librarian.library_exists(traktor_dir):
            conf.library_dir = traktor_dir

        return render.index(traktor_dir, sys.platform)


class Initialize:
    def GET(self):
        if hasattr(conf, "library_dir"):
            initialize_library(conf.library_dir)

        response = {"status": "ok"}
        return json.dumps(response)


class CheckTraktor:
    def GET(self):
        if not librarian.is_traktor_running():
            response = {"status": "ok"}
        else:
            response = {"status": "error", "message": "Please quit Traktor first."}

        return json.dumps(response)


class Clean:
    def GET(self):
        if librarian.is_traktor_running():
            response = {"status": "error", "message": "Please quit Traktor first."}
        else:
            cleaner = Cleaner(Library.instance())
            cleaner.remove_duplicates()
            logger.debug(u"Duplicate removal complete")

            response = cleaner.get_result()
            response["status"] = "ok"

        return json.dumps(response)


class CleanConfirm:
    def GET(self):
        try:
            response = {"status": "ok", "backup": Library.instance().flush()}
        except:
            response = {"status": "error"}

        return json.dumps(response)


class Export:

    def POST(self):
        request = json.loads(web.data())

        if librarian.is_traktor_running():
            response = {"status": "error", "message": "Please quit it first."}
        else:
            conf.remove_orphans = request["remove_orphans"]
            export_worker = threading.Thread(target=self._export, args=(request["destination"],))
            export_worker.start()
            response = {"status": "ok"}

        return json.dumps(response)

    def _export(self, destination):
        Exporter(Library.instance(), destination).export()


class ExportCancel:
    def GET(self):
        if Exporter.instance:
            Exporter.instance.cancel()
            initialize_library(conf.library_dir)  # re-initialize library to discard in memory changes done by Exporter

            response = {"status": "ok"}
        else:
            response = {"status": "error"}

        return json.dumps(response)


class ExportVolumeScan:
    def GET(self):
        volumes = get_volumes()
        response = {"status": "ok", "volumes": volumes}

        return json.dumps(response)


class ExportStatus:
    def GET(self):
        if Exporter.instance:
            messages = Exporter.instance.get_messages()

            if messages is None:
                status = "end"
                initialize_library(conf.library_dir)  # re-initialize library to discard in memory changes done by Exporter
            else:
                status = "ok"

            response = {"status": status, "messages": messages}
        else:
            response = {"status": "ok"}

        return json.dumps(response)


class ChoosePath:
    def POST(self):
        request = json.loads(web.data())

        directory = webview.create_file_dialog(webview.FOLDER_DIALOG)

        if directory:
            directory = directory[0]
            response = {"status": "ok", "directory": directory}

            if "traktor_check" in request.keys() and request["traktor_check"]:
                if librarian.library_exists(directory):
                    conf.library_dir = directory
                else:
                    response = {"status": "error", "message": "Traktor library not found in {}".format(directory)}
        else:
            response = {"status": "cancel"}

        return json.dumps(response)


def get_volumes():
    volumes = [p.mountpoint.split("/")[-1] for p in psutil.disk_partitions()
               if p.mountpoint != "/" and p.mountpoint.startswith("/Volumes") and "rw" in p.opts]

    return volumes


def initialize_library(directory):
    def _start_thread():
        Library(directory)

    worker = threading.Thread(target=_start_thread)
    worker.start()



def start_webserver(port, server_semaphore, tries=0):
    import socket

    web.debug = False
    #web.config.log_toprint = False
    #web.config.log_tofile = False

    class WebApplication(web.application):
        def run(self, port=8080, *middleware):
            func = self.wsgifunc(*middleware)
            return web.httpserver.runsimple(func, ('localhost', port))

    try:
        global http_port
        webapp = WebApplication(urls, globals())
        http_port = port
        server_semaphore.release()

        webapp.run(port)

    except socket.error as e:  # retry to start a server on a different port if the current pot is occupied
        if tries > 10:  # give up after 10th try
            raise e
        else:
            server_semaphore.acquire()
            start_webserver(port + 1, tries + 1)


server_semaphore = threading.Semaphore(0)

if __name__ == "__main__":
    start_webserver(8080, server_semaphore)