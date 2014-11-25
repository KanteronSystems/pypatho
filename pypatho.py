from tornado.options import define, options
import tornado.web
import tornado.gen
import tornado.httpserver

from StringIO import StringIO

import os
import sqlite3

#Internal Functions Come Now...
import opts

#Functions

def isAlreadyThere(filehash):
    cur = db.cursor()
    cur.execute("SELECT * FROM files WHERE hash=:hash and written=1",
        {"hash": filehash})
    res=cur.fetchone()
    if res==None:
        return 0
    else:
        return 1


#Handlers
class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class OjeteHandler(BaseHandler):
    def get(self):
        self.write("Ojete, world")

class HashHandler(BaseHandler):
    def get(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM files WHERE hash=:hash and written=1",
            {"hash": options.hashdemo})
        res=cur.fetchone()
        if res==None:
            self.write('0') 
        else:
            self.write('1')


#App
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", OjeteHandler),
            (r"/si", HashHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = sqlite3.connect(options.database)

def main():
    tornado.options.parse_command_line()
    print 'Serving on ' + str(options.port) + '...'
    print 'Connecting to database ' + options.database
    #con = sqlite3.connect(options.database)
    #cur = con.cursor()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
        main()
