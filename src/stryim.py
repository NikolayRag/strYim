#  todo 92 (flv) +0: make class non-static
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
class SinkRTMP():
	cFile= None

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

		self.sink.add(self.videoTag(2,True))
		self.sink.close()




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
		tagOut.extend( (dataLen+11).to_bytes(4, 'big') )	#data+tagOut length

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


#  todo 93 (flv) +0: make data flow without overhead
	#VIDEODATA
	@staticmethod
	def videoTag(_type, _key, _data=b'', _stamp=0, _ctime=0):
		if _type==0:
			_data= MuxFLV.headDCR


		tagA= MuxFLV.tag(9, _stamp, b'', len(_data)+5) #prepare tag for data substitution
		tagA[-1:-1]= [
			  bytes([(16 if _key else 32) +7])			#frame type (1=key, 2=not) and codecID (7=avc)
			, bytes([_type])							#AVCPacketType
			, (_ctime).to_bytes(3, 'big', signed=True)	#Composition time
			, _data
		]

		return b''.join(tagA)











import subprocess, threading, time, socket
from .mp4RecoverExe import *


class StreamFFRTMP():
	faac= None
	f264= None
	fflv= None
	flvStamp= 0.

	tcp= None
	tcpSock= None
	hHead0= Atom(preset=(1080,30,0))
	hHead1= Atom(preset=-1)

	initFlag= None


	def __init__(self):
		self.faac= open('D:/yi/restore/stryim/sss.aac', 'wb')
		self.f264= open('D:/yi/restore/stryim/sss.h264', 'wb')
		self.fflv= open('D:/yi/restore/stryim/sss.flv', 'wb')
		self.flvStamp= 0.
		self.flvRate= 1001./30

		self.f264.write(b'\x00\x00\x00\x01' +self.hHead0.data +b'\x00\x00\x00\x01' +self.hHead1.data)

		self.fflv.write(MuxFLV.header(audio=False))
		self.fflv.write(MuxFLV.metaTag())
		self.fflv.write(MuxFLV.videoTag(0,True))
		self.fflv.write(MuxFLV.videoTag(1,True, self.hHead0.lenB()+self.hHead0.data+self.hHead1.lenB()+self.hHead1.data))
		return



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

		self.tcp.sendall(self.h264[(1080,30,'low')])

		self.initFlag.set()


	def go(self, _atom):
		if _atom.type!=None: #not sound
			self.f264.write(b'\x00\x00\x00\x01' +_atom.data)
			flvTag= MuxFLV.videoTag(1,_atom.type=='IDR', _atom.lenB()+_atom.data, int(self.flvStamp))
			self.fflv.write(flvTag)

			self.flvStamp+= self.flvRate
		else:
			self.faac.write(_atom.data)
		return



		if self.tcp and _atom.type!=None:
			try:
				self.tcp.sendall(b'\x00\x00\x00\x01' +_atom.data)
			except:
				self.tcp= None


	def stop(self):
		self.faac.close()
		self.f264.close()

		self.fflv.write(MuxFLV.videoTag(2,True))
		self.fflv.close()



		tcp= self.tcp
		self.tcp= None
		if tcp:
			tcp.close()

#		self.tcpSock.close()







#  todo 94 (app) +2: handle start-stop
import sublime, sublime_plugin
from .mp4RecoverExe import *
from .byteTransit import *
from .kiYiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None, None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	

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
		kiLog.states(False, False, True, 'KiYiListener')
		kiLog.states(True, True, True, 'mp4RecoverExe')

		selfIP= KiTelnet.defaults(address='192.168.42.1')

		if KiYi[0]:
			kiLog.warn('Already')
			return

		

		KiYi[1]= StreamFFRTMP()

		restoreO= mp4RecoverExe(KiYi[1].go)
		buffer= byteTransit(restoreO.parse, 1000000)



#		buffer.context('123')
#		KiTelnet('cat /tmp/fuse_d/DCIM/105MEDIA/L0010639.MP4', buffer.add).result()
#		buffer.context(None)
#		return



		KiYi[0]= KiYiListener()
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

		KiYi[1].stop()
