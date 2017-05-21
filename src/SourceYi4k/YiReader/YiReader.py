import logging, inspect, socket, threading

from .YiListener import *
from .YiPy import *
from .YiSide import *


'''
YiReader drives Yi4k to provide .mp4 raw byte stream,
 which will then be passed to the mp4 recoverer.
Telnet must be enabled in the camera, as it is used
 to run Python agent at camera side.

YiReader flow, with .start():

* send agent to camera
* run agent at camera side
* connect to agent
	* recieve data
		* send data to provided callback
'''
class YiReader():
	yiAddr= None
	yiPort= None
	yiListener= None

	errorCB= None

	
	'''
	Init with specified camera address and port.
	Port will be used by camera twice, incremented, to listen over TCP:
		- first time to recieve Python code to execute YiAgent (by YiPy)
		- then by YiPy to set streaming connection
	'''
	def __init__(self, addr='192.168.42.1', port=1231, _dataCB=None, _ctxCB=None, _stateCB=None, _errorCB=None):
		self.yiAddr= addr
		self.yiPort= port

		def agentErrorCB(_type, _meta):
			if callable(_stateCB) and _type==YiData.OVERFLOW:
				_stateCB('Low camera bandwidth, data is skipped')

		yiData= YiData(_dataCB, _ctxCB, agentErrorCB)
		self.yiListener= YiListener(addr, port, yiData.restore)

		self.errorCB= callable(_errorCB) and _errorCB


		logging.info('Reader inited')



	'''
	Run YiAgent at camera and run it.
	Provided _ctxCB and _dataCB are callbacks to listen detected .mp4 stream.
	Stream will be recieved in chunks of arbitrary length (certainly x512Kb).
	At start of each block _ctxCB will be called, provided with
	 {context, length} dict. Then binary data is sequentally passed
	 to _dataCB until next chunk.
	'''
	def start(self):
		if self.yiListener.isAlive():
			logging.warning('Already running')

			return False


		if self.yiRunAgent():
			self.yiListener.start()

			return True



	'''
	Close connection to YiAgent. That will stop YiAgent and YiReader normally.
	'''
	def stop(self):
		self.yiListener.stop()
		
		logging.info('Close')




#PRIVATE


	'''
	Run YiAgent and related code at Yi4k.
	'''
	def yiRunAgent(self, _agentRoute='check'):
		agentSrc= []
		agentSrc.extend( inspect.getsourcelines(YiData)[0] )
		agentSrc.extend( inspect.getsourcelines(YiSock)[0] )
		agentSrc.extend( inspect.getsourcelines(YiAgent)[0] )
		agentSrc.extend( inspect.getsourcelines(YiCleanup)[0] )
		agentSrc= ''.join(agentSrc)

		yipy= YiPy(self.yiAddr, self.yiPort+1) #Use different ports for YiPy and YiAgent to avoid interferention
		if not yipy.run('%s\nYiAgent(%d).%s()' % (agentSrc, self.yiPort, _agentRoute)):
			logging.error('Running Yi')
			return False


		def yiRuntimeErrorCB(res):
			self.yiListener.stop()

			if res!=b'':
				logging.error(res)

				self.errorCB and self.errorCB(res)

		yipy.wait(yiRuntimeErrorCB)


		return True

