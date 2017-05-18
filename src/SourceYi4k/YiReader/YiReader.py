import logging, inspect, socket, threading

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
# =todo 290 (streaming, fix, ffmpeg, exploit) +1: /289; separate thread; streaming to rtmp cause reading delay
class YiReader():
	yiAddr= None
	yiSocket= None

	runFlag= False


	
	'''
	Init with specified camera address and port.
	Port will be used by camera twice, incremented, to listen over TCP:
		- first time to recieve Python code to execute YiAgent (by YiPy)
		- then by YiPy to set streaming connection
	'''
	def __init__(self, addr='192.168.42.1', port=1231):
		self.yiAddr= addr
		self.yiPort= port
		
		logging.info('Reader inited')



	'''
	Run YiAgent at camera and run it.
	Provided _ctxCB and _dataCB are callbacks to listen detected .mp4 stream.
	Stream will be recieved in chunks of arbitrary length (certainly x512Kb).
	At start of each block _ctxCB will be called, provided with
	 {context, length} dict. Then binary data is sequentally passed
	 to _dataCB until next chunk.
	'''
	def start(self, _dataCB=None, _ctxCB=None, _stateCB=None, _errorCB=None):
		if self.yiSocket:
			logging.warning('Already running')

			return False


		yiData= YiData(_dataCB, _ctxCB, _stateCB)

		threading.Timer(0, lambda:self.yiListen(yiData.restore)).start()
		
		threading.Timer(0, lambda:self.yiRunAgent(_errorCB)).start()


		return True



	'''
	Close connection to YiAgent. That will stop YiAgent and YiReader normally.
	'''
	def stop(self):
		if not self.yiSocket:
			return
		
		logging.info('Close')

		self.runFlag= False



#PRIVATE


	'''
	Connect to YiAgent and listen back.
	'''
	def yiListen(self, _cb=None):
		self.runFlag= True
		self.yiSocket= None

		logging.info('Connecting to nc')
		for n in range(5):
			try:
				self.yiSocket= socket.create_connection((self.yiAddr,self.yiPort), 1)
				break
			except:
				None
			

		if not self.yiSocket:
			logging.error('Not connected')
			return

		self.yiSocket.settimeout(1)


		logging.info('Yi begin')

		while self.runFlag:
			try:
				res= self.yiSocket.recv(16384)
			except socket.timeout:
				continue
			except Exception as x:
				logging.info('Yi end: %s' % x)
				break

			callable(_cb) and _cb(res)


		self.yiSocket.shutdown(socket.SHUT_RDWR)
		self.yiSocket.close()
		self.yiSocket= None



	'''
	Run YiAgent and related code at Yi4k.
	'''
	def yiRunAgent(self, _agentRoute='check', errorCB=None):
		agentSrc= []
		agentSrc.extend( inspect.getsourcelines(YiData)[0] )
		agentSrc.extend( inspect.getsourcelines(YiSock)[0] )
		agentSrc.extend( inspect.getsourcelines(YiAgent)[0] )
		agentSrc= ''.join(agentSrc)

		yipy= YiPy(self.yiAddr, self.yiPort+1) #Use different ports for YiPy and YiAgent to avoid interferention
		if not yipy.run('%s\nYiAgent(%d).%s()' % (agentSrc, self.yiPort, _agentRoute)):
			logging.error('Running Yi')
			return


		res= yipy.wait()

		self.runFlag= False	#socket could be orphan


		if res:
			logging.error(res)

			callable(errorCB) and errorCB()


		return not res

