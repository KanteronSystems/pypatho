from tornado.options import define, options
import tornado.web
import tornado.gen
import tornado.httpserver

from skimage import io

from StringIO import StringIO

import datetime
import os
import sqlite3
import imghdr
from hashlib import md5

#Internal Functions Come Now...
import opts

#How about some processing algorithms?
import processors

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

class HomeHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

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
            path = options.uploadpath + "/original/" + hashresult[0:3]
            #TODO Integrar el chequeo de directorio al arranque? Mantenerlo 'PORSIACA'?
            if not os.path.exists(path):
                os.makedirs(path)
            output = open(path + '/' + hashresult + '.jpg', 'wb')
            output.write(file1['body'])
            output.close()
            #Procesemos
            image = io.imread(path + '/' + hashresult + '.jpg')
            #UNO
            if not os.path.exists(options.processedpath + '/1/' + hashresult[0:3]):
                os.makedirs(options.processedpath + '/1/' + hashresult[0:3])
                imagepro = processors.processHED(image, 1)
                io.imsave(options.processedpath + '/1/' +  hashresult[0:3] + '/' + hashresult + '.jpg', imagepro)
            #DOS
            if not os.path.exists(options.processedpath + '/2/' + hashresult[0:3]):
                os.makedirs(options.processedpath + '/2/' + hashresult[0:3])
                imagepro = processors.processHED(image, 2)
                io.imsave(options.processedpath + '/2/' + hashresult[0:3] + '/' + hashresult + '.jpg', imagepro)
            #TRES
            if not os.path.exists(options.processedpath + '/3/' + hashresult[0:3]):
                os.makedirs(options.processedpath + '/3/' + hashresult[0:3])
                imagepro = processors.processHED(image, 3)
                io.imsave(options.processedpath + '/3/' + hashresult[0:3] + '/' + hashresult + '.jpg', imagepro)
            #OMG, no tengo perdon de $DEITY
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

class ProcessFileHandler(BaseHandler):
    def get(self, input):
        algo = 1
        path = options.processedpath + '/' + str(algo) 
        fullpath = path + '/' + input[0:3] + '/' + input + '.jpg'
        if os.path.exists(fullpath):
            File = open(fullpath,"r")
            self.set_header("Content-Type", 'image/jpeg')
            self.write(File.read())
            File.close()
        else:
            self.write('VAYA HOMBRE! ' + fullpath)


#App
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/api/v1/hash/check/([a-fA-F\d]{32})", HashHandler),
            #(r"/api/hash/check/(\w+)", HashHandler),
            (r"/api/v1/file/post", PostFileHandler),
            (r"/api/v1/file/get/([a-fA-F\d]{32}).jpg", GetFileHandler),
            (r"/api/v1/file/process/1/([a-fA-F\d]{32}).jpg", ProcessFileHandler),
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
    #TODO Chequear que todas las rutas existen
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
        main()
