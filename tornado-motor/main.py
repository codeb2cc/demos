#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, with_statement

import motor

from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado import web, ioloop


define('port', default=8000, type=int)


class TestHandler(web.RequestHandler):
    @web.asynchronous
    def get(self):
        self.write('<ul>')

        db = self.settings['db']
        db.messages.find().sort([('_id', -1)]).each(self.on_message)

    def on_message(self, message, error):
        if error:
            raise web.HTTPServer(500, error)
        elif message:
            self.write('<li>%s</li>' % message['msg'])
        else:
            self.write('</ul>')
            self.finish()

    @web.asynchronous
    def post(self):
        msg = self.get_argument('msg')

        db = self.settings['db']
        db.messages.insert({'msg': msg}, callback=self.on_save)

    def on_save(self, result, error):
        if error:
            raise web.HTTPServer(500, error)
        else:
            self.write('OK')
            self.finish()


class Application(web.Application):
    def __init__(self, db):
        handlers = [
            (r'/', TestHandler),
        ]
        web.Application.__init__(self, handlers, db=db)


def main():
    # I've tried to use `open` to test with Tornado's `gen.coroutine` and
    # `Futures`. But the api does not return a `Future` and `motor`'s own tests
    # won't pass also. The lib seems to be broken partially.
    # Anyway, the `open_sync` with callback style works fine.
    db = motor.MotorClient().open_sync().test
    app = Application(db=db)

    server = HTTPServer(app)
    server.listen(options.port)

    print(">>> Running on %d ..." % options.port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    options.parse_command_line()

    main()

