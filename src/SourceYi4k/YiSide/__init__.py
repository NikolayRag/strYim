'''
Capture full-band stream from Yi4k camera.
YiData(port) should be run at Yi4k side.
Camera will wait for connection on port provided,
and then stream data to it, when loop-record is on.
'''

from .YiData import *
from .YiSock import *
from .YiAgent import *
