'''
Continuously read loop-recorded files as soon as record is on.
Reading is started every time loop recording is detected.

Agent is run at Yi4k side.

Flow:
* continouosly detect file being recorded
* read tail
	* till next file in queue is recorded
		* repeat read
'''
class YiAgent():
	camRoot= '/tmp/fuse_d/DCIM'
	camMask= '???MEDIA/L???????.MP4'

	liveOldAge= 4 #maximum number of seconds to consider tested file 'live'


	import socket, threading, time, os, glob
	tcpSocket= None



	def __init__(self, _port, _test=None):
		if not self.tcpInit(_port):
			return

		if _test:
			self.test()
		else:
			self.check()



	def tcpInit(self, _port):
		cListen= YiAgent.socket.socket()
		cListen.setsockopt(YiAgent.socket.SOL_SOCKET, YiAgent.socket.SO_REUSEADDR, 1)

		try:
			cListen.bind(('0.0.0.0',_port))
		except Exception as x:
			print('error: %s' % x)
			return

		cListen.listen(1)
		cListen.settimeout(5)

		try:
			c, a= cListen.accept()
		except Exception as x:
			print('error: %s' % x)
			return

		self.tcpSocket= c

		return True



	def send(self, _data):
		try:
			self.tcpSocket.send(_data)
			return True
		except:
			None



	'''
	Close socket.
	If called while running, cause exception in sending data,
	 resulting stop execution.
	'''
	def close(self):
		if not self.tcpSocket:
			return

		self.tcpSocket.close()



	'''
	Normal execution after caller is connected.
	'''
	def check(self):
		fileNew= fileOld= False
		
		#terminated by socket
		while True:
			#check port state
			if not self.send(b''):
				print('closed')
				return


			fileOld= fileNew
			fileNew= self.detectActiveFile()
			if not self.send(str(fileNew)):
				print('error')
				return

			YiAgent.time.sleep(.5)

		return



	'''
	Return file assumed to be currently recorded in Loop mode.
	That is file with specific name, updated recently.
	'''
	def detectActiveFile(self):
		mp4Mask= "%s/%s" % (self.camRoot, self.camMask)

		lastStamp= 0
		activeFile= None
		
		for mp4File in YiAgent.glob.glob(mp4Mask):
			mtime= YiAgent.os.path.getmtime(mp4File)
			
			if mtime>lastStamp:
				lastStamp= mtime
				activeFile= mp4File

		if not activeFile:
			return

		if YiAgent.time.time()-lastStamp > self.liveOldAge: #too old
			return


		return {'fname': activeFile, 'size': int(YiAgent.os.path.getsize(activeFile))}



	def xxx(self):
		f= open('/dev/random', 'rb')
		
		block= 100000
		for n in range(10):
			b= f.read(block)
			
			if not self.send(b):
				print('stop')
				return

			if len(b)<block:
				break









	'''
	Test function.
	'''
	def test(self):
		YiAgent.threading.Timer(10, self.close).start()


		f= open('/dev/random', 'rb')
		
		block= 100000
		while True:
			b= f.read(block)
			
			if not self.send(b):
				print('stop')
				return

			if len(b)<block:
				break
