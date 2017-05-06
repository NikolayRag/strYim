from .YiReader import *
from .YiDecoder import *
#from .YiControl import *


'''
Complete Yi4k driver.
Handle camera settings, operation mode (loop record),
 capture full-band stream from Yi4k camera and decode it into Atom sequence.

Splitted in two sections:
- control camera config and running state
- continuously read camera's .mp4 data and decode it to 264/aac Atoms
'''
class Yi4k():
	yiReader= None
	yiDecoder= None

	activeCtx= None


	'''
	Connect muxer to send Atoms to.
	'''
	def __init__(self, _muxCB=None):
		self.yiReader= YiReader()
		self.yiDecoder= Mp4Recover(_muxCB)



	'''
	Apply camera settings and start streaming data into mux callback.

	'''
	def start(self):
		self.yiReaderRes= self.yiReader.start(self.dataCB, self.ctxCB, self.stateCB)


	def stop(self):
		self.yiReader.yiClose()






	def dataCB(self, _data):
		self.yiDecoder.add(_data, self.activeCtx)



	def ctxCB(self, _ctx):
		self.activeCtx= _ctx['ctx']

		logging.debug('Context %d' % self.activeCtx)



	def stateCB(self, _state, _data):
		logging.debug('State: %d' % _state)

		#if _state==YiData.STOP:
		#	cMux.stop()