#! /usr/bin/env python2.7
from SimpleHTTPServer import SimpleHTTPRequestHandler
import BaseHTTPServer


class MyHTTPRequestHandler(SimpleHTTPRequestHandler):

    """Request handler that translates /path into /path.html.

    This is similar to how GitHub pages are served.

    """

    def translate_path(self, path):
        if '.' not in path and path != '/':
            path += '.html'
        return SimpleHTTPRequestHandler.translate_path(self, path)


if __name__ == '__main__':
    BaseHTTPServer.test(MyHTTPRequestHandler, BaseHTTPServer.HTTPServer)
