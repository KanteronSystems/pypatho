from tornado.options import options,define

#Networking 
define("port", default=8080, help="Port to run the server")

#Varios database
define("database", default="process.db", help="Sqlite database to connect")
define("hashdemo", default="78190a01d271953214c57f55c47f27490", help="File hash to test")
