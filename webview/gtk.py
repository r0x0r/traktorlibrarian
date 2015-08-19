"""
(C) 2014 Roman Sirokov
Licensed under BSD license

http://github.com/r0x0r/pywebview/
"""

import logging

logger = logging.getLogger(__name__)


try:
    # Try GTK 3
    from gi.repository import Gtk as gtk
    from gi.repository import Gdk
    from gi.repository import WebKit as webkit
except ImportError as e:
    import_error = True
    logger.warn("PyGObject is not found", exc_info=True)
else:
    import_error = False


class BrowserView:
    instance = None

    def __init__(self, title, url, width, height, resizable, fullscreen):
        BrowserView.instance = self
        window = gtk.Window(title=title)

        window.set_size_request(width, height)
        window.set_resizable(resizable)
        window.set_position(gtk.WindowPosition.CENTER)

        if fullscreen:
            window.fullscreen()

        window.connect("delete-event", gtk.main_quit)

        scrolled_window = gtk.ScrolledWindow()
        window.add(scrolled_window)

        webview = webkit.WebView()
        scrolled_window.add_with_viewport(webview)
        window.show_all()
        webview.load_uri(url)

        self.window = window
        self.webview = webview


    def show(self):
        gtk.main()

    def open_file_dialog(self, open_folder):
        dialog = gtk.FileChooserDialog("Please choose a file", self,
                                       gtk.FileChooserAction.OPEN,
                                       (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
                                        gtk.STOCK_OPEN, gtk.ResponseType.OK))

        response = dialog.run()
        if response == gtk.ResponseType.OK:
            return dialog.get_filename()
        elif response == gtk.ResponseType.CANCEL:
            return None

        dialog.destroy()


    def load_url(self, url):
        self.webview.load_uri(url)



def create_window(title, url, width, height, resizable, fullscreen):
    browser = BrowserView(title, url, width, height, resizable, fullscreen)
    browser.show()


def load_url(url):
    if BrowserView.instance is not None:
        BrowserView.instance.load_url(url)
    else:
        raise Exception("Create a web view window first, before invoking this function")


def open_file_dialog(open_folder):
    if BrowserView.instance is not None:
        BrowserView.instance.open_file_dialog(open_folder)
    else:
        raise Exception("Create a web view window first, before invoking this function")
