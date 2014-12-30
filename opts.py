from tornado.options import options, define

# Networking
define("port", default=8080, help="Port to run the server")

# Database Framework
define("dbengine", default="mongodb", help="Database engine used to store information")
define("dburl", default="mongodb://testing:testing@ds027491.mongolab.com:27491/pypatho", help="Database url to connect")

# Varios database
define("database", default="process.db", help="Sqlite database to connect")
define("hashdemo", default="78190a01d271953214c57f55c47f2749", help="File hash to test")

#Object storage
define("container_name", default="pypatho-test", help="Container where files get stored")
define("endpoint", default="https://ams01.objectstorage.softlayer.net", help="Endpoint for your object storage")
define("storageuser", default="", help="User for your object storage")
define("storagekey", default="", help="Password for your object storage")
