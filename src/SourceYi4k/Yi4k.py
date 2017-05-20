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

	atomCB= None
	signalCB= None

	idle= True


	'''
	Init source.
	If not provided, Atom and signal callbacks can be linked lately.
	Streaming will start as soon as camera goes loop-recording by start().
	Stopping camera rater manually or by stop() stops YiReader as well.
	'''
	def __init__(self, atomCB=None, signalCB=None):
		self.link(atomCB, signalCB)

		self.yiReader= YiReader(self.yiAddr)
		self.yiDecoder= Mp4Recover(self.atomLoopbackCB)

		self.yiControl= YiControl(self.yiAddr, self.cameraStopCB)




	'''
	Link external consumer to send Atoms to.
	It can be done on fly.
	'''
	def link(self, atomCB=None, signalCB=None):
		self.atomCB= callable(atomCB) and atomCB
		self.signalCB= callable(signalCB) and signalCB




	'''
	Apply camera settings and start streaming data into mux callback.
	
	WARNING: Stryim doesn't check if camera data matches muxer settings.
	'''
#  todo 272 (Yi, config) +0: add 60 fps
#  todo 273 (Yi, config) +0: add 1440 format
	def start(self, fps=30, fmt=1080):
		if not self.yiReader.start(self.readerDataCB, self.readerContextCB, self.readerStateCB, self.readerErrCB):
			logging.error('Camera cannot be accessed by telnet')
			return


		if not self.yiControl.start(fps, fmt):
			logging.error('Camera cannot start')

			self.yiReader.stop()
			return


		logging.info('Starting %d' % fmt)

		self.idle= False





	'''
	Stop camera.
	yiReader also stopped, as well as if camera stops manually.
	'''
	def stop(self):
		self.yiControl.stop()




	def isIdle(self):
		return self.idle



#### PRIVATE




	def readerDataCB(self, _data):
		self.yiDecoder.add(_data, self.activeCtx)



	def readerContextCB(self, _ctx):
		self.activeCtx= _ctx['ctx']

		logging.debug('Context %d, %d bytes' % (self.activeCtx, _ctx['len']))



	def readerStateCB(self, _state, _data):
		logging.info('State: %d' % _state)

#		self.signalCB and self.signalCB(_state, _data)




	'''
	Internal loopback for Atoms from Mp4Recover.
	'''
	def atomLoopbackCB(self, _atom):
		self.atomCB and self.atomCB(_atom)



	def cameraStopCB(self):
		logging.info('Camera stops')

		self.yiReader.stop()

		self.idle= True


	def readerErrCB(self, _res):
		if _res==False:
			logging.error('Camera lost')
			self.idle= True
		else:
			logging.error('Streaming error')
			self.yiControl.stop()

