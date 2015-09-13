import webview
import threading
import guiserver


def start_ui(url):
    webview.create_window("Traktor Librarian", url, resizable=False)


if __name__ == '__main__':
    server = threading.Thread(target=guiserver.start_webserver, args=(41345,))
    server.daemon = False
    server.start()

    start_ui("http://localhost:{}/".format(guiserver.http_port))
