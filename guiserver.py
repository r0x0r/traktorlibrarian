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
    '/', "Index",
)

render = web.template.render('templates/')


class Index:

    traktor_lib = None

    def GET(self):
        conf["filelog"] = False  # disable file logging
        conf["debug"] = True  # disable verbose messages
        Index.logger = configure_logger(logging.getLogger(__name__))

        traktor_dir = librarian.get_traktor_dir().replace("\\", "\\\\")

        if librarian.library_exists(traktor_dir):
            conf["library_dir"] = traktor_dir

        return render.index(traktor_dir, sys.platform)

    def POST(self):
        request = json.loads(web.data())

        if request["action"] == "initialize":
            if librarian.is_traktor_running():
                response = {"status": "error", "message": "Traktor is running. Please quit it first."}
            else:
                if Index.traktor_lib is None and "library_dir" in conf:
                    Index.library_semaphore = threading.Semaphore(0)
                    Index.traktor_lib = Library(conf["library_dir"])
                    Index.library_semaphore.release()

                response = {"status": "ok"}

            volumes = self._get_volumes()
            response["volumes"] = volumes

            return json.dumps(response)

        elif request["action"] == "check":
            if librarian.is_traktor_running():
                response = {"status": "error", "message": "Traktor is running. Please quit it first."}
            else:
                response = {"status": "ok"}

            return json.dumps(response)

        elif request["action"] == "scan":
            if librarian.is_traktor_running():
                response = {"status": "error", "message": "Traktor is running. Please quit it first."}
            else:
                if Index.library_semaphore is None or Index.traktor_lib is None:
                    Index.traktor_lib = Library(conf["library_dir"])

                Index.library_semaphore.acquire()
                Index.cleaner = Cleaner(Index.traktor_lib)
                Index.library_semaphore.release()

                Index.cleaner.remove_duplicates()
                self.logger.debug(u"Duplicate removal complete")

                response = Index.cleaner.get_result()
                response["status"] = "ok"

            return json.dumps(response)

        elif request["action"] == "remove":
            try:
                response = {"status": "ok", "backup": Index.traktor_lib.flush()}
            except:
                response = {"status": "error"}

            return json.dumps(response)

        elif request["action"] == "check_volumes":
            volumes = self._get_volumes()
            response = {"status": "ok", "volumes": volumes}

            return json.dumps(response)

        elif request["action"] == "export":
            if librarian.is_traktor_running():
                response = {"status": "error", "message": "Please quit it first."}
            else:
                conf["remove_orphans"] = request["remove_orphans"]

                if Index.library_semaphore is None or Index.traktor_lib is None:
                    Index.traktor_lib = Library(conf["library_dir"])

                Index.library_semaphore.acquire()
                Index.exporter = Exporter(Index.traktor_lib, request["destination"])
                Index.library_semaphore.release()

                Index.exporter.export()
                response = {"status": "ok"}

            return json.dumps(response)

        elif request["action"] == "cancel":
            Index.exporter.cancel()
            response = {"status": "ok"}

            return json.dumps(response)

        elif request["action"] == "export_status":
            messages = Index.exporter.get_messages()

            if messages is None:
                status = "end"
            else:
                status = "ok"

            response = {"status": status, "messages": messages}
            return json.dumps(response)

        elif request["action"] == "open_file_dialog":
            directory = webview.create_file_dialog(webview.FOLDER_DIALOG)[0]
            response = {"status": "ok", "directory": directory}

            if "traktor_check" in request.keys() and request["traktor_check"]:
                if librarian.library_exists(directory):
                    conf["library_dir"] = directory
                else:
                    response = {"status": "error", "message": "Traktor library not found in {}".format(directory)}

            return json.dumps(response)

    def _get_volumes(self):
        volumes = [p.mountpoint.split("/")[-1] for p in psutil.disk_partitions()
                   if p.mountpoint != "/" and p.mountpoint.startswith("/Volumes") and "rw" in p.opts]

        return volumes


def start_webserver(port, server_semaphore, tries=0):
    import socket

    class WebApplication(web.application):
        def run(self, port=8080, *middleware):
            func = self.wsgifunc(*middleware)
            return web.httpserver.runsimple(func, ('localhost', port))

    try:
        global http_port
        webapp = WebApplication(urls, globals())
        http_port = port
        server_semaphore.release()

        webapp.run(port=port)
    except socket.error as e:  # retry to start a server on a different port if the current pot is occupied
        if tries > 10:  # give up after 10th try
            raise e
        else:
            start_webserver(port + 1, tries + 1)


if __name__ == "__main__":
    server_semaphore = threading.Semaphore(0)
    start_webserver(8080, server_semaphore)