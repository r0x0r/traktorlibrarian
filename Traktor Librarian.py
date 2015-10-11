import os
import sys
import webview
import threading
import guiserver


def start_ui(url):
    webview.create_window("Traktor Librarian", url, resizable=False)


if __name__ == '__main__':
    server_semaphore = threading.Semaphore(0)
    server = threading.Thread(target=guiserver.start_webserver, args=(41345, server_semaphore))
    server.daemon = True
    server.start()

    server_semaphore.acquire()
    start_ui("http://localhost:{}/".format(guiserver.http_port))
    server_semaphore.release()

    try:
        guiserver.Index.exporter.cancel()
    except:
        pass

    os._exit(0)
