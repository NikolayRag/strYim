from .YiReader import *
from .YiDecoder import *
#from .YiControl import *


'''
Complete Yi4k driver.
Capture full-band stream from Yi4k camera.

Splitted in two sections:
- continuously read camera's .mp4 data and decode it to 264/aac Atoms
- control camera running state and config
'''