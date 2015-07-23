"""Pathology image analizer webservice
by Alvaro G."""

from tornado.options import options
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop

from swiftclient import Connection

# Sin usar ?
# from PIL import Image
# from skimage import io

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
# def isalreadythere(filehash):
#     pass


# Handlers
class BaseHandler(tornado.web.RequestHandler):
    """Base handler for all other methods"""
    pass


class TestingHandler(BaseHandler):
    """Fake testing handler, probably will get deleted"""
    pass


class HomeHandler(BaseHandler):
    """Serves the home page"""
    def get(self):
        self.render("index.html")


class HashHandler(BaseHandler):
    """Check the existence of a certain file on the database, via its hash"""
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
    """Receives a file via POST method"""
    def post(self):
        # Pending use of apikey
        # apikey = self.get_argument('apikey')
        file1 = self.request.files['file1'][0]
        # original_fname = file1['filename']
        hashresult = md5(file1['body']).hexdigest()
        if imghdr.what(file1, file1['body']) != 'jpeg':
            self.write('No JPEG! BAD!')
        else:
            self.write(hashresult)
            self.application.swift.put_object(container=options.container_name,
                                              obj=hashresult + '.jpg',
                                              contents=file1['body'],
                                              content_type='image/jpeg')
            coll = self.application.mongodb.files
            files_doc = {'_id': hashresult,
                         'datetime': datetime.datetime.now()}
            coll.insert(files_doc)


class GetFileHandler(BaseHandler):
    """Serves file via a GET method"""
    def get(self, filehash):
        coll = self.application.mongodb.files
        files_doc = coll.find_one({"_id": filehash})
        if files_doc:
            imagefile = self.application.swift.get_object(
                container=options.container_name,
                obj=filehash + '.jpg')[1]
            self.set_header("Content-Type", 'image/jpeg')
            self.write(imagefile)
        else:
            self.write('MAAAAL')


class ProcessFileHandler(BaseHandler):
    """Asks for processing certain file"""
    def get(self, process, filehash):
        # TODO: Guardar los PNG procesados y 'avisar' a la base de datos
        coll = self.application.mongodb.files
        files_doc = coll.find_one({"_id": filehash})
        if files_doc:
            target = self.application.swift.get_object(
                container=options.container_name,
                obj=filehash + '.jpg')[1]
            processed = processors.processor(process, target)
            self.set_header("Content-Type", 'image/png')
            self.write(processed)
        else:
            self.write('no existe' + filehash)


class ListImagesHandler(BaseHandler):
    """List images in database"""
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
    """Application initialization"""
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/list(?:/([0-9]*))?", ListImagesHandler),
            (r"/api/v1/hash/check/([a-fA-F\d]{32})", HashHandler),
            # (r"/api/hash/check/(\w+)", HashHandler),
            (r"/api/v1/file/post", PostFileHandler),
            (r"/api/v1/file/get/([a-fA-F\d]{32}).jpg", GetFileHandler),
            (r"/api/v1/file/process/([\d]{2})/([a-fA-F\d]{32}).png",
             ProcessFileHandler),
            (r"/testing/", TestingHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        conn = pymongo.Connection(options.dburl)
        self.mongodb = conn.pypatho

        self.swift = Connection(
            authurl=options.endpoint + "/auth/v1.0",
            user=options.storageuser,
            key=options.storagekey,
            auth_version="1",
            insecure=True)


def main():
    """Main thread"""
    tornado.options.parse_command_line()
    print 'Serving on ' + str(options.port) + '...'
    # TODO Chequear que todas las rutas existen
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
