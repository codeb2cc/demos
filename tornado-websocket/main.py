# -*- coding:utf-8 -*-

import tornado

from tornado.httpserver import HTTPServer
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.options import define, options


define('port', default=8000, help='run on the given port', type=int)


class IndexHandler(RequestHandler):
    def get(self):
        self.write('OK')


class EchoWebSocket(WebSocketHandler):
    def open(self):
        print 'WebSocket opend'

    def on_message(self, message):
        self.write_message(u'You said: ' + message)

    def on_close(self):
        print 'WebSocket closed'


class Application(Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler),
            (r'/echo/', EchoWebSocket),
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    tornado.options.parse_command_line()

    app = Application()

    server = HTTPServer(app)
    server.listen(options.port)

    print '>>> Runing on %d ...' % options.port
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()

