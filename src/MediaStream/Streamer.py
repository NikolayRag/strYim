from .Atom import *
from .Mux import *
from .Sink import *
try:
	from Stat import *
except:
	from src.Stat import *

import threading, queue
import logging


#  todo 284 (feature, streaming) +0: Make audio/video mixer (switcher) as a Source-to-Streamer fabric
#  todo 330 (feature, review) +0: review Sink statistics
'''
Main streaming controller.
Route Atoms from linked Source to managed destination.
'''
StreamIdle= 0
StreamAir= 1
StreamWarn= 2
StreamErr= 3

class Streamer(threading.Thread):
	stat= None

	source= None

	sink= None
	atomsQ= None

	live= True

	stateCB= None


	'''
	Init settings.
	Streaming destination will be opened, wainting for muxed Atoms.
	'''
	def __init__(self):
		threading.Thread.__init__(self)

		self.stat= Stat()
		self.stat.trigger(StatTrigger(fn=self.stat.max, steps=[10,20,30,50,80,130,200,350,550,900,1500,2300,3800,6100,10000], cb=self.statCB))

		self.atomsQ= queue.Queue()

		self.start()



	def begin(self, _dst, _header, _fps):
		if self.sink:
			logging.warning('Stream already running')
			return

		self.sink= self.initSink(_dst, _header, _fps)

		logging.info('Streaming to %s' % _dst)

		return True



	'''
	(re)Link Source.
	Calling without arguments unlink Source without stopping streaming.
	 Other Source can be linked lately.

#  todo 283 (feature, streaming) +0: define Source abstract superclass.
	Source should have .link(atomCB) method.
	'''
	def link(self, _source=None):
		self.source and self.source.link()

		if _source and callable(_source.link):
			_source.link(self.atomPort)
			self.source= _source



	'''
	Close destination.
	'''
	def end(self):
		sink= self.sink
		self.sink= None
		sink and sink.close()

		logging.info('Closed')
		self.stateCB and self.stateCB(StreamIdle, 0)


	'''
	Close and stop streamer.
	It cant be restarted.
	'''
	def kill(self):
		self.end()
		
		self.live= False



	def setStateCB(self, _cb):
		self.stateCB= callable(_cb) and _cb



### PRIVATE



	'''
	Create muxer and sink based on destination.
	
	Set FLV/rtmp general streaming if destination begins with 'rtmp://..'.
	'tcp://..' tells to send over TCP, which is suitable with ffmpeg.
	Otherwise destination should be valid file path to save.

	For non-rtmp desstination use ['.FLV'|'.264'|'.AAC'] extension
	 to define output format.
	'''
	def initSink(self, _dst, _header, _fps):
		_dst= '/'.join(_dst.split('\\'))
		protocol= _dst.split(':/')
		ext= _dst.split('.')


		MuxFLV.defaults(fps=_fps, srate=48000)
		muxer= MuxFLV
		sink= SinkNet

		if protocol[0] not in ['rtmp', 'udp', 'tcp']:
			if protocol[0] in ['srv']:
				sink= SinkServer
			else:
				sink= SinkFile

				if len(ext)>1 and (ext[-1] in ['264', 'h264']):
					muxer= MuxH264
				if len(ext)>1 and ext[-1]=='aac':
					muxer= MuxAAC

# =todo 307 (streaming, mux, sink) +0: Get stream prefix from source
		return sink(_dst, muxer(_header), self.sinkStateCB)




	'''
	Function is passed to Source's link()
	'''
	def atomPort(self, _atom):
		if isinstance(_atom, Atom):
			self.atomsQ.put(_atom)

			self.stat.add(self.atomsQ.qsize())

	

	'''
	Thread cycle.
	Spool Atoms queue to muxer+sink
	'''
	def run(self):
		while self.live:
			cAtom= None
			try:
				cAtom= self.atomsQ.get(timeout=.1)
			except queue.Empty:
				pass


			if self.sink and cAtom:
				if not self.sink.add(cAtom):
					logging.error('Sink is dead')
			
					self.end()



			self.stat.add(self.atomsQ.qsize())



	'''
	Get statistic
	'''
	def statCB(self, _val, _raise):
		if _raise:
			if _val==750:
				logging.error('Low streaming bandwidth, data is jammed')
				
			logging.debug('Atoms over: %s' % _val)
		else:
			logging.debug('Atoms under: %s' % _val)



	def sinkStateCB(self, _error, _state):
		if not self.stateCB:
			return

		if _error:
			self.stateCB(StreamErr, 'Sink error')
			return


		warningMsg= None

		if _state<.2:
			warningMsg= 'underflow'

		if _state>.8:
			warningMsg= 'overflow'

		self.stateCB([StreamAir, StreamWarn][warningMsg!=None], warningMsg, _state)
