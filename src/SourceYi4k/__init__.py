'''
Capture full-band stream from Yi4k camera.
Splitted in two sections:
- continuously read camera's .mp4 data and decode it to 264/aac Atoms
- control camera running state and config
'''

# -todo 266 (YiAgent, check) +1: check camera die
#  todo 261 (YiAgent, check) +0: set camera settings

from .YiReader import *
