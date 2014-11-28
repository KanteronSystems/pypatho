from tornado.options import define, options
import tornado.web
import tornado.gen
import tornado.httpserver

from StringIO import StringIO

import datetime
import os
import sqlite3
import imghdr
from hashlib import md5

#Internal Functions Come Now...
import opts

#Functions

def isAlreadyThere(filehash):
    cur = self.db.cursor()
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
    def get(self, input):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM files WHERE hash=:hash and written=1",
            {"hash": input})
        res=cur.fetchone()
        if res==None:
            self.write('NO') 
        else:
            self.write('OK')

class PostFileHandler(BaseHandler):
    def post(self):
        apikey = self.get_argument('apikey')
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        hashresult=md5(file1['body']).hexdigest()
        if imghdr.what(file1,file1['body']) != 'jpeg':
            self.write('No JPEG! BAD!')
        else:
            self.write('JPEG! Very Good!' + hashresult)
            directory = "uploads/original/" + hashresult[0:3]
            if not os.path.exists(directory):
                os.makedirs(directory)
            output = open(directory + '/' + hashresult + '.jpg', 'wb')
            output.write(file1['body'])
            output.close()
            cur = self.db.cursor()
            cur.execute("INSERT OR REPLACE INTO files VALUES(?,?,1)", (hashresult, datetime.datetime.now()));
            self.db.commit()

class GetFileHandler(BaseHandler):
    def get(self, input):
        path = options.uploadpath + '/original'
        fullpath = path + '/' + input[0:3] + '/' + input + '.jpg'
        if os.path.exists(fullpath):
            File = open(fullpath,"r")
            self.set_header("Content-Type", 'image/jpeg')
            self.write(File.read())
            File.close()
        else:
            self.write('MAAAAL')

#App
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", OjeteHandler),
            (r"/api/v1/hash/check/([a-fA-F\d]{32})", HashHandler),
            #(r"/api/hash/check/(\w+)", HashHandler),
            (r"/api/v1/file/post", PostFileHandler),
            (r"/api/v1/file/get/([a-fA-F\d]{32}).jpg", GetFileHandler),
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
