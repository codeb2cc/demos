# -*- coding:utf-8 -*-

import time
import functools

import tornado

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import Application, RequestHandler
from tornado.web import asynchronous
from tornado.options import define, options


define('port', default=8000, help='run on the given port', type=int)


class IndexHandler(RequestHandler):
    def get(self):
        self.write('OK')


class CallbackHandler(RequestHandler):
    @asynchronous
    def get(self):
        io_loop = IOLoop.instance()
        io_loop.add_callback(functools.partial(self.callback, 3))

        print '<< GET'

    def callback(self, count=0):
        print 'Callback #%d' % count

        if count > 0:
            io_loop = IOLoop.instance()
            io_loop.add_callback(functools.partial(self.callback, count - 1))
        else:
            self.write('Callback OK')
            self.finish()


class TimeoutHandler(RequestHandler):
    @asynchronous
    def get(self):
        io_loop = IOLoop.instance()
        io_loop.add_timeout(time.time() + 5, self.timeout)

        print '<< GET'

    def timeout(self):
        print 'Timeout'
        self.write('Timeout OK')
        self.finish()


class DuplicatedHandler(RequestHandler):
    _duplicated = dict()

    def prepare(self):
        self.key = self.get_argument('key', '_')

    @asynchronous
    def get(self):
        print 'With `key`: %s' % self.key
        if DuplicatedHandler._duplicated.has_key(self.key):
            assert isinstance(DuplicatedHandler._duplicated[self.key], list)

            DuplicatedHandler._duplicated[self.key].append((self, self.callback))
            print 'Duplicated'
        else:
            DuplicatedHandler._duplicated[self.key] = []
            ioloop = IOLoop.instance()
            ioloop.add_timeout(time.time() + 10, self.timeout)
            print 'New'

    def timeout(self):
        print 'Func `timeout`'
        if DuplicatedHandler._duplicated.has_key(self.key):
            assert isinstance(DuplicatedHandler._duplicated[self.key], list)

            while len(DuplicatedHandler._duplicated[self.key]):
                print '#'
                request, handler = DuplicatedHandler._duplicated[self.key].pop()
                handler()

        DuplicatedHandler._duplicated.pop(self.key)

        self.callback()

    def callback(self):
        print 'Func `callback`'
        self.write('Callback OK')
        self.finish()


class Application(Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler),
            (r'/callback', CallbackHandler),
            (r'/timeout', TimeoutHandler),
            (r'/duplicated', DuplicatedHandler),
        ]
        tornado.web.Application.__init__(self, handlers, debug=True)


def main():
    tornado.options.parse_command_line()

    app = Application()

    server = HTTPServer(app)
    server.listen(options.port)

    print '>>> Runing on %d ...' % options.port
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()

