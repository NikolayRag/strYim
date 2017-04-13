'''
Capture full-band stream from Yi4k camera.
Stream is readed from loop-recorded 

#  todo 260 (YiAgent, check) +0: catch recording stops or cannot start
#  todo 261 (YiAgent, check) +0: set camera settings


Reader flow:

# =todo 257 (feature, YiAgent) +0: Send agent to camera
# =todo 258 (feature, YiAgent) +0: Run agent at camera
# =todo 259 (feature, YiAgent) +0: Make camera agent
* send agent to camera
* run agent at camera side
* connect to agent
	* recieve Atom data
		* decode AAC


'''

from .yiReader import *
