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
Yi4kIdle= 0
Yi4kSteady= 1
Yi4kAir= 2
Yi4kWarn= 3
Yi4kErr= 4

class Yi4k():
	yiAddr= '192.168.42.1'

	yiReader= None
	yiDecoder= None
	yiControl= None

	activeCtx= None

	atomCB= None
	stateCB= None

	flagState= Yi4kIdle


	'''
	Init source.
	If not provided, Atom and signal callbacks can be linked lately.
	Streaming will start as soon as camera goes loop-recording by start().
	Stopping camera rater manually or by stop() stops YiReader as well.
	'''
	def __init__(self, atomCB=None, signalCB=None):
		self.link(atomCB, signalCB)

		self.yiReader= YiReader(self.yiAddr, 1232, self.readerDataCB, self.readerContextCB, self.readerStateCB, self.readerErrCB)
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
	def start(self, _preset, flat=False):
		self.setState(Yi4kSteady, '')

		threading.Timer(0, lambda: self.startActual(_preset, flat)).start()


	def startActual(self, _preset, flat):
		if not self.yiReader.start():
			self.setState(Yi4kErr, 'Camera cannot be accessed by telnet')
			return


		if not self.yiControl.start(_preset, flat):
			self.setState(Yi4kErr, 'Camera cannot start')

			self.yiReader.stop()
			return


		logging.info('Starting %s' % _preset['yiRes'])


		self.setState(Yi4kAir, '')




	'''
	Stop camera.
	yiReader also stopped, as well as if camera stops manually.
	'''
	def stop(self):
		return self.yiControl.stop()




	def isIdle(self):
		if self.flagState==Yi4kIdle:
			return True

		if self.flagState==Yi4kErr:
			return True



#### PRIVATE




	def readerDataCB(self, _data):
		self.yiDecoder.add(_data, self.activeCtx)



	def readerContextCB(self, _ctx):
		self.activeCtx= _ctx['ctx']

		logging.debug('Context %d, %d bytes' % (self.activeCtx, _ctx['len']))



	def readerStateCB(self, _type, _msg):
		self.setState(Yi4kWarn, _msg)



	'''
	Internal loopback for Atoms from Mp4Recover.
	'''
	def atomLoopbackCB(self, _atom):
		self.atomCB and self.atomCB(_atom)



	def cameraStopCB(self):
		logging.info('Camera stops')

		self.yiReader.stop()

		self.setState(Yi4kIdle, '')



	def readerErrCB(self, _res):
# -todo 328 (Yi, control) +0: handle camera lost state withon YiControl
		msg= ''

		if _res==False:
			msg= 'Camera lost'
		else:
			msg= 'Streaming error'
			self.yiControl.stop()


		self.setState(Yi4kErr, msg)



	def setStateCB(self, _cb):
		self.stateCB= callable(_cb) and _cb



	def setState(self, _state, _msg=''):
		self.flagState= _state

		if _state==Yi4kErr:
			logging.error(_msg)

		if _state==Yi4kWarn:
			logging.warning(_msg)



		self.stateCB and self.stateCB(_state, _msg)
