from tornado.options import options
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop

from skimage import io

import pymongo

import datetime
import os
import imghdr
from hashlib import md5

# Internal Functions Come Now...
import opts

# How about some processing algorithms?
import processors


# Functions
def isAlreadyThere(filehash):
    pass


# Handlers
class BaseHandler(tornado.web.RequestHandler):
    pass


class HomeHandler(BaseHandler):
    def get(self):
        self.render("index.html")


class HashHandler(BaseHandler):
    def get(self, filehash):
        coll = self.application.mongodb.files
        files_doc = coll.find_one({"_id": filehash})
        if files_doc:
            # Borramos la id para serializar?
            # del files_doc["_id"]
            # self.write(files_doc)
            self.write("OK")
        else:
            self.set_status(404)
            self.write({"error": "Image not found!"})


class PostFileHandler(BaseHandler):
    def post(self):
        # Pending use of apikey
        # apikey = self.get_argument('apikey')
        file1 = self.request.files['file1'][0]
        # original_fname = file1['filename']
        hashresult = md5(file1['body']).hexdigest()
        if imghdr.what(file1,file1['body']) != 'jpeg':
            self.write('No JPEG! BAD!')
        else:
            self.write('JPEG! Very Good!' + hashresult)
            path = options.uploadpath + "/original/" + hashresult[0:3]
            # TODO Integrar el chequeo de directorio al arranque? Mantenerlo 'PORSIACA'?
            if not os.path.exists(path):
                os.makedirs(path)
            output = open(path + '/' + hashresult + '.jpg', 'wb')
            output.write(file1['body'])
            output.close()
            coll = self.application.mongodb.files
            files_doc = {'_id': hashresult, 'datetime': datetime.datetime.now()}
            coll.insert(files_doc)


class GetFileHandler(BaseHandler):
    def get(self, input):
        path = options.uploadpath + '/original'
        fullpath = path + '/' + input[0:3] + '/' + input + '.jpg'
        if os.path.exists(fullpath):
            imagefile = open(fullpath,"r")
            self.set_header("Content-Type", 'image/jpeg')
            self.write(imagefile.read())
            imagefile.close()
        else:
            self.write('MAAAAL')


class ProcessFileHandler(BaseHandler):
    def get(self, process, filehash):
        processedfile = options.processedpath + '/' + process + '/' + filehash[0:3] + '/' + filehash + '.png'
        processedfilepath = options.processedpath + '/' + process + '/' + filehash[0:3]
        originalfile = options.uploadpath + '/original/' + filehash[0:3] + '/' + filehash + '.jpg'

        if os.path.exists(processedfile):
            imagefile = open(processedfile, "r")
            self.set_header("Content-Type", 'image/png')
            self.write(imagefile.read())
            imagefile.close()
        elif not os.path.exists(processedfile) and os.path.exists(originalfile):
            if not os.path.exists(processedfilepath):
                os.makedirs(processedfilepath)
            processed = processors.processor(process, originalfile)
            io.imsave(processedfile, processed)
            imagefile = open(processedfile, "r")
            self.set_header("Content-Type", 'image/png')
            self.write(imagefile.read())
            imagefile.close()
        else:
            self.write('no existe' + originalfile)


class ListImagesHandler(BaseHandler):
    def get(self, page):
        page = int(page) if page else '0'
        pagination = 20
        pagebegin = page * pagination
        coll = self.application.mongodb.files
        files_doc = coll.find().limit(pagination).skip(int(pagebegin))
        self.render(
            "list.html",
            title="Pypatho - Processed file list",
            # header = "Processed files",
            images=files_doc
        )


# App
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/list(?:/([0-9]*))?", ListImagesHandler),
            (r"/api/v1/hash/check/([a-fA-F\d]{32})", HashHandler),
            # (r"/api/hash/check/(\w+)", HashHandler),
            (r"/api/v1/file/post", PostFileHandler),
            (r"/api/v1/file/get/([a-fA-F\d]{32}).jpg", GetFileHandler),
            (r"/api/v1/file/process/([\d]{2})/([a-fA-F\d]{32}).png", ProcessFileHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        conn = pymongo.Connection(options.dburl)
        self.mongodb = conn.pypatho


def main():
    tornado.options.parse_command_line()
    print 'Serving on ' + str(options.port) + '...'
    # TODO Chequear que todas las rutas existen
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
        main()
