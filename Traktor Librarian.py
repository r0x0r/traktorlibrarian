import sys
from threading import Thread, Lock
import webview
from time import sleep


if sys.platform == "darwin":
    import six
    import packaging
    import packaging.requirements
    import packaging.version
    import packaging.specifiers

from guiserver import start_webserver
from logger import get_logger

logger = get_logger(__name__)
server_lock = Lock()


def url_ok(url, port):
    from httplib import HTTPConnection

    try:
        conn = HTTPConnection(url, port)
        conn.request("GET", "/")
        r = conn.getresponse()
        return r.status == 200
    except:
        logger.exception("Server not started")
        return False

if __name__ == '__main__':
    logger.debug("Starting server")
    t = Thread(target=start_webserver, args=(41345,))
    t.daemon = True
    t.start()
    logger.debug("Checking server")

    while not url_ok("127.0.0.1", 41345):
        sleep(0.1)

    logger.debug("Server started")
    webview.create_window("Traktor Librarian", "http://127.0.0.1:41345", min_size=(640, 480))

    try:
        guiserver.Index.exporter.cancel()
    except:
        pass



