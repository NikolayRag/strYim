from .YiReader import *
from .YiDecoder import *
from .YiControl import *


'''
Complete Yi4k driver.
Handle camera settings, operation mode (loop record),
 capture full-band stream from Yi4k camera and decode it into Atom sequence.

Splitted in two sections:
- control camera config and running state
- continuously read camera's .mp4 data and decode it to 264/aac Atoms

Generally, reading and decoding is bound to camera record state.
'''
class Yi4k():
	yiAddr= '192.168.42.1'

	yiReader= None
	yiDecoder= None
	yiControl= None

	activeCtx= None

	signalCB= None


	'''
	Connect muxer to send Atoms to.
	Streaming will start as soon as camera goes loop-recording by start().
	'''
	def __init__(self, _muxCB=None, _signalCB=None):
		self.signalCB= callable(_signalCB) and _signalCB

		self.yiReader= YiReader(self.yiAddr)
		self.yiDecoder= Mp4Recover(_muxCB)

		self.yiControl= YiControl(self.yiAddr, self.yiReader.yiClose)




	'''
	Apply camera settings and start streaming data into mux callback.
	If not forced, start is suppressed if camera is already recording.
	
	WARNING: Stryim doesn't check if camera data matches muxer settings.
	'''
#  todo 272 (Yi, config) +0: add 60 fps
#  todo 273 (Yi, config) +0: add 1440 format
	def start(self, force=False, fps=30, fmt=1080):
		if not self.yiControl.start(fps, fmt):
			return

		res= self.yiReader.start(self.dataCB, self.ctxCB, self.stateCB)
		if not res:
			self.yiControl.stop()

		return res



	'''
	Stop camera.
	yiReader also stopped, as well as if camera stops manually.
	'''
	def stop(self):
		self.yiControl.stop()




#### PRIVATE




	def dataCB(self, _data):
		self.yiDecoder.add(_data, self.activeCtx)



	def ctxCB(self, _ctx):
		self.activeCtx= _ctx['ctx']

		logging.debug('Context %d' % self.activeCtx)



	def stateCB(self, _state, _data):
		logging.info('State: %d' % _state)

#		self.signalCB and self.signalCB(_state, _data)
