from hashlib import md5
from datetime import datetime,timedelta
import xxhash
import os

#filetohash='resources/pato.png'
filetohash='/Users/andor/Downloads/root.iso'

print('File: ' + filetohash)
print('Size: ' + str(os.path.getsize(filetohash)/1024) + 'KBytes')

print('File + hash:')

before=datetime.now()
file=open(filetohash, 'rb')
filecontent=file.read()
hashresult=md5(filecontent).hexdigest()
file.close()
after=datetime.now()
difftime=after-before
print('MD5 : ' + hashresult + ' - ' + str(difftime.total_seconds())) + ' secs'

before=datetime.now()
before=datetime.now()
file=open(filetohash, 'rb')
filecontent=file.read()
hashresult=xxhash.xxh64(filecontent).hexdigest()
file.close()
after=datetime.now()
difftime=after-before
print('XX  : ' + hashresult + ' - ' + str(difftime.total_seconds())) + ' secs'


print('Hash only:')

file=open(filetohash, 'rb')
filecontent=file.read()
file.close()

before=datetime.now()
hashresult=md5(filecontent).hexdigest()
after=datetime.now()
difftime=after-before
print('MD5 : ' + hashresult + ' - ' + str(difftime.total_seconds())) + ' secs'

before=datetime.now()
hashresult=xxhash.xxh64(filecontent).hexdigest()
after=datetime.now()
difftime=after-before
print('XX  : ' + hashresult + ' - ' + str(difftime.total_seconds())) + ' secs'
