from .kiLog import *

'''
Mux-suitable sink for sending binary data to file
'''
class SinkFile():
	cFile= None

	def __init__(self, _fn):
		self.cFile= open(_fn, 'wb')

	def add(self, _data):
		self.cFile.write(_data)

	def close(self):
		self.cFile.close()




'''
Mux-suitable sink for sending binary data to RTMP
'''
import subprocess, threading, socket
class SinkRTMP():
	rtmp= ''

	tcp= None


	def __init__(self, _rtmp):
		self.rtmp= _rtmp


		ffport= 2345
		threading.Timer(0, lambda: self.serverInit(ffport)).start()
		self.tcp= self.tcpInit(ffport)

		print('inited')




	def add(self, _data):
		if not self.tcp:
			return

		try:
			self.tcp.sendall(_data)
		except:
			kiLog('Socket error')
			self.tcp= None


	def close(self):
		tcp= self.tcp
		self.tcp= None
		if tcp:
			tcp.close()




	#private

	def serverInit(self, _ffport):
#  todo 104 (clean, release) +0: use 'current' folder for release and hide ffmpeg
#  todo 105 (sink, unsure) -1: hardcode RTMP protocol
		subprocess.call('D:/yi/restore/ff/ffmpeg -re -i tcp://127.0.0.1:%d?listen -c copy -f flv %s' % (_ffport, self.rtmp), shell=False)


	def tcpInit(self, _ffport):
		return socket.create_connection(('127.0.0.1',_ffport))

