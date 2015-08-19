import os
import sys
import librarian
import psutil

from clean import Cleaner
from export import Exporter
from library import Library
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
        traktor_dir = librarian.get_traktor_dir().replace("\\", "\\\\")
        Index.traktor_lib = Library(traktor_dir)
        conf["library_dir"] = traktor_dir

        return render.index(traktor_dir)

    def POST(self):
        request = json.loads(web.data())

        if request["action"] == "check":
            if librarian.is_traktor_running():
                response = {"status": "error", "reason": "running"}
            elif not librarian.library_exists(request["library_dir"]):
                response = {"status": "error", "reason": "nolibrary"}
            else:
                #conf["library_dir"] = request["library_dir"]
                conf["filelog"] = False # disable file logging
                conf["verbose"] = False # disable verbose messages
                response = {"status": "ok"}

            return json.dumps(response)
        elif request["action"] == "scan":
            if librarian.is_traktor_running():
                response = {"status": "error", "reason": "running"}
            elif not librarian.library_exists(request["library_dir"]):
                response = {"status": "error", "reason": "nolibrary"}
            else:
                #conf["library_dir"] = request["library_dir"]
                conf["filelog"] = False  # disable file logging
                conf["verbose"] = False  # disable verbose messages

                Index.traktor_lib = Library(conf["library_dir"])
                Index.cleaner = Cleaner(Index.traktor_lib)
                Index.cleaner.remove_duplicates()

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
            volumes = [p.mountpoint.split("/")[-1] for p in psutil.disk_partitions()
                       if p.mountpoint != "/" and p.mountpoint.startswith("/Volumes")]
            response = {"status": "ok", "volumes": volumes}

            return json.dumps(response)

        elif request["action"] == "export":
            conf["remove_orphans"] = False
            Index.traktor_lib = Library(conf["library_dir"])
            Index.exporter = Exporter(Index.traktor_lib, request["destination"])

            Index.exporter.export()
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
            folder = webview.open_file_dialog(True)

            response = {"status": "ok", "folder": folder}

            return json.dumps(response)




def start_webserver(port, tries=0):
    import socket

    class WebApplication(web.application):
        def run(self, port=8080, *middleware):
            func = self.wsgifunc(*middleware)
            return web.httpserver.runsimple(func, ('localhost', port))


    try:
        global http_port
        webapp = WebApplication(urls, globals())
        http_port = port
        webapp.run(port=port)
    except socket.error as e:  # retry to start a server on a different port if the current pot is occupied
        if tries > 10:  # give up after 10th try
            raise e
        else:
            start_webserver(port + 1, tries + 1)


if __name__ == "__main__":
    start_webserver(8080)