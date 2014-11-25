import sqlite3

#database = 'process.db'
#con = None
#
#hashdemo = '78190a01d271953214c57f55c47f2749'
#
##Connection is mine
#con = sqlite3.connect(database)
#cur = con.cursor()
#
#Busca perrito
#cur.execute("SELECT * FROM files WHERE hash=:hash and written=1",
#    {"hash": hashdemo})
#res=cur.fetchone()
#
#if res==None:
#    print('No hay nada')
#else:
#    print('Algo hay')


def isAlreadyThere(filehash):
    cur.execute("SELECT * FROM files WHERE hash=:hash and written=1",
        {"hash": filehash})
    res=cur.fetchone()
    if res==None:
        return 0
    else:
        return 1

#print('Hash inventado ' + str(isAlreadyThere('ojete')))
#print('Hash de verdad ' + str(isAlreadyThere('78190a01d271953214c57f55c47f2749')))

#con.close()
