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
	tcp= None
	tcpSock= None

	initFlag= None


	def __init__(self):
		self.tcp= None


		self.initFlag= threading.Event()

		ffport= 2345
		threading.Timer(0, lambda: self.tcpInit(ffport)).start()
		threading.Timer(0, lambda: self.serverInit(ffport)).start()

		self.initFlag.wait();


	def serverInit(self, _ffport):
		None
		subprocess.call('D:/yi/restore/ff/ffmpeg -re -i tcp://localhost:%d -vcodec copy -f flv rtmp://localhost:5130/live/yi/' % _ffport, shell=False)
#		subprocess.call('D:/yi/restore/ff/ffmpeg -re -i tcp://localhost:%d -vcodec copy http://localhost:8090/yi.ffm' % _ffport, shell=False)


	def tcpInit(self, _ffport):
		self.tcpSock= socket.socket()

		self.tcpSock.bind(('127.0.0.1',_ffport))

		self.tcpSock.listen(1)
		self.tcp, a= self.tcpSock.accept()

		self.initFlag.set()


	def add(self, _data):
		if not self.tcp:
			return

		try:
			self.tcp.sendall(b'\x00\x00\x00\x01' +_atom.data)
		except:
			kiLog('Socket error')
			self.tcp= None


	def close(self):
		tcp= self.tcp
		self.tcp= None
		if tcp:
			tcp.close()

		self.tcpSock.close()























'''
FLV Muxer class
Requires Sink to be specified
'''
class MuxFLV():
# =todo 90 (flv) +0: construct META
	headMeta= b'\x02\x00\nonMetaData\x08\x00\x00\x00\x0b\x00\x08duration\x00@D=\x91hr\xb0!\x00\x05width\x00@\x9e\x00\x00\x00\x00\x00\x00\x00\x06height\x00@\x90\xe0\x00\x00\x00\x00\x00\x00\rvideodatarate\x00@\xc7\x00\xcd\xe0\x00\x00\x00\x00\tframerate\x00@=\xf6\xff\x825\xd3D\x00\x0cvideocodecid\x00@\x1c\x00\x00\x00\x00\x00\x00\x00\x0bmajor_brand\x02\x00\x04isom\x00\rminor_version\x02\x00\x03512\x00\x11compatible_brands\x02\x00\x10isomiso2avc1mp41\x00\x07encoder\x02\x00\rLavf57.57.100\x00\x08filesize\x00A\x8d5\x11\x10\x00\x00\x00\x00\x00\t'
# =todo 91 (flv) +0: construct AVCDecoderConfigurationRecord
	headDCR= b'\x01\x4d\x40\x33\xff\xe1\x00\x34\x27\x4d\x40\x33\x9a\x64\x03\xc0\x11\x3f\x2c\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea\x60\xe8\x60\x00\xb7\x18\x00\x02\xdc\x6c\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00\x5b\x8d\x97\x79\x70\x78\x44\x22\x52\xc0\x01\x00\x04\x28\xee\x38\x80'

	sink= None


	def __init__(self, _sink):
		self.flvStamp= 0.
		self.flvRate= 1001./30


		self.sink= _sink

		if not self.sink:
			return

		self.sink.add(self.header(audio=False))
		self.sink.add(self.metaTag())
		self.sink.add(self.videoTag(0,True))


	def add(self, _atom):
		if not self.sink:
			return

		if _atom.type!=None: #not sound
			flvTag= self.videoTag(1,_atom.type=='IDR', _atom.data, int(self.flvStamp))
			self.sink.add(flvTag)

			self.flvStamp+= self.flvRate


	def stop(self):
		if not self.sink:
			return

		self.sink.add( self.videoTag(2,True,stamp=int(self.flvStamp)) )
		self.sink.close()



	#private

	#FLVTAG, size ended
	def tag(self, _type, _stamp=0, _data=[b'']):
		if _stamp<0 or _stamp>2147483647: #0 to 7fffffff 
			kiLog.err('Stamp out of range: %s' % _stamp)
			_stamp= 0


		_stamp= (_stamp).to_bytes(4, 'big')

		dataLen= 0
		for cD in _data:
			dataLen+= len(cD)

		tagOut= [
			  bytes([_type]) 				#tag type (8=audio, 9=video, ..)
			, (dataLen).to_bytes(3, 'big')	#data lenth
			, _stamp[1:]					#stamp ui24
			, _stamp[0:1]					#stamp upper byte
			, b'\x00\x00\x00'				#streamID
		]

		tagOut.extend(_data)
		tagOut.extend([ (dataLen+11).to_bytes(4, 'big') ])	#data+tagOut length

		return tagOut


	#FLV header: "FLV\x01..."
	def header(self, video=True, audio=True):
		video= 1* (video==True)
		audio= 3* (audio==True)

		return b'\x46\x4c\x56\x01' +bytes([video+audio]) +b'\x00\x00\x00\x09' +b'\x00\x00\x00\x00'


	#META tag
	def metaTag(self):
		meta= self.tag(18, 0, [self.headMeta])

		return b''.join(meta)


	#VIDEODATA
	def videoTag(self, _type, _key, _data=b'', stamp=0, comptime=0):
		if _type==0:
			_data= self.headDCR

		dataLen= b''
		if _type==1:
			dataLen= len(_data).to_bytes(4, 'big')


		avcData= [
			  bytes([(16 if _key else 32) +7])			#frame type (1=key, 2=not) and codecID (7=avc)
			, bytes([_type])							#AVCPacketType
			, (comptime).to_bytes(3, 'big', signed=True)	#Composition time
			, dataLen
			, _data
		]

		tagA= self.tag(9, stamp, avcData)	#prepare tag for data substitution


		return b''.join(tagA)






'''
h264 test Muxer class
Requires Sink to be specified
'''
class MuxH264():

	sink= None


	def __init__(self, _sink):
		self.sink= _sink

		if not self.sink:
			kiLog.err('Sink not specified')
			return

	def add(self, _atom):
		if not self.sink:
			return

		if _atom.type!=None: #not sound
			self.sink.add(b'\x00\x00\x00\x01' +_atom.data)


	def stop(self):
		if not self.sink:
			return

		self.sink.close()




'''
AAC test Muxer class
Requires Sink to be specified
'''
class MuxAAC():

	sink= None


	def __init__(self, _sink):
		self.sink= _sink

		if not self.sink:
			kiLog.err('Sink not specified')
			return


	def add(self, _atom):
		if not self.sink:
			return

		if not _atom.type: #sound
			self.sink.add(_atom.data)


	def stop(self):
		if not self.sink:
			return

		self.sink.close()













import sublime, sublime_plugin
from .mp4RecoverExe import *
from .byteTransit import *
from .yiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None, None, None, None, None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	

# =todo 94 (app) +2: handle start-stops
	def cbConn(self, _mode):
		kiLog.ok('Connected' if _mode else 'Disconnected')
	def cbLive(self, _mode):
		if _mode==1:
			kiLog.ok('Live')
		if _mode==-1:
			kiLog.ok('Dead')
	def cbAir(self, _mode):
		if _mode==1:
			kiLog.warn('Air On')
		if _mode==0:
			kiLog.warn('Air Off')
		if _mode==-1:
			kiLog.err('Air bad')

	def run(self, _edit):
		kiLog.states(True, True, True)
		kiLog.states(False, False, True, 'YiListener')
		kiLog.states(True, True, True, 'mp4RecoverExe')

		selfIP= KiTelnet.defaults(address='192.168.42.1')

		if KiYi[0]:
			kiLog.warn('Already')
			return

		

		muxFlash= KiYi[2]= MuxFLV(SinkFile('D:/yi/restore/stryim/sss+.flv'))
		muxH264= KiYi[3]= MuxH264(SinkFile('D:/yi/restore/stryim/sss+.h264'))
		muxAAC= KiYi[4]= MuxAAC(SinkFile('D:/yi/restore/stryim/sss+.aac'))

		def streamRelay(_atom):
			muxFlash.add(_atom)
			muxH264.add(_atom)
			muxAAC.add(_atom)

		restoreO= mp4RecoverExe(streamRelay)
# =todo 95 (bytes) +0: move use of byteTransit inside mp4RecoverExe
		buffer= byteTransit(restoreO.parse, 1000000)
		KiYi[0]= YiListener()
		KiYi[0].start(self.cbConn, self.cbLive)
		KiYi[0].live(buffer, self.cbAir)


#ast.literal_eval(aa)
class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0].stop()
		KiYi[0]= None

		KiYi[2].stop()
		KiYi[3].stop()
		KiYi[4].stop()
