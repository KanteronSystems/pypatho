"""Database testing tool"""
import sqlite3
from hashlib import md5
from datetime import datetime


def main():
    """Main"""
    database = 'process.db'
    # con = None

    filetohash = 'resources/pato.png'

    # Connection is mine
    con = sqlite3.connect(database)
    cur = con.cursor()

    # Read Hash
    fileopen = open(filetohash, 'rb')
    filecontent = fileopen.read()
    hashresult = md5(filecontent).hexdigest()
    fileopen.close()

    # Inserta
    cur.execute("REPLACE INTO files VALUES(:hash,:date,1)",
                {"hash": hashresult, "date": datetime.now()})
    con.commit()

    # Adieu
    con.close()


if __name__ == "__main__":
    main()
