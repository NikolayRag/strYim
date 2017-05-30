class Mux():
	None




from .AAC import *
import logging


'''
FLV Muxer class
Requires Sink to be specified
'''
class MuxFLV(Mux):
	stat= {'frames': 0, 'aac': 0}

	stampCurrent= 0.

	stampVideoNext= 0.
	rateVideo= 1000./ (30000./1001) #29.97fps frame duration
	stampAudioNext= 0
	rateAudio= 1000./ 48000

	useAudio= True

	sink= None


	@staticmethod
	def defaults(fps=None, srate=None):
		if fps:
			MuxFLV.rateVideo= 1000./fps
		if srate:
			MuxFLV.rateAudio= 1000./srate


	def __init__(self, _sink, fps=None, audio=True, srate=None):
		self.stat= {'frames': 0, 'aac': 0}

		self.stampCurrent= 0.

		self.stampVideoNext= 0.
		if fps:
			self.rateVideo= 1000./fps
		self.stampAudioNext= 0.
		if srate:
			self.rateAudio= 1000./srate


		self.sink= _sink

		if not self.sink:
			logging.error('Sink not specified')
			return


		self.useAudio= audio

		self.flush( self.header(audio=self.useAudio) )
		self.flush( self.videoTag(0,True,self.videoDCR()) )
		if self.useAudio:
			self.flush( self.audioTag(0,self.audioSC()) )


	def add(self, _atom):
		if not self.sink:
			return

		if _atom.typeAVC and _atom.AVCVisible:
			self.stat['frames']+= 1
			flvTag= self.videoTag(1, _atom.AVCKey, _atom.data, self.stampV())
			self.flush(flvTag)

		if self.useAudio and _atom.typeAAC:
			if len(_atom.data)>2040:
				logging.warning('Too big AAC found, skipped: %d' % len(_atom.data))
				return

			self.stat['aac']+= 1
			flvTag= self.audioTag(1, _atom.data, self.stampA(_atom.AACSamples))
			self.flush(flvTag)


	def stop(self):
		logging.info('%d frames, %d aac' % (self.stat['frames'], self.stat['aac']))
		if not self.sink:
			return

		self.flush( self.videoTag(2,True,stamp=self.stampV()) )
		self.sink.close()

		self.sink= None



	#private

	def flush(self, _data):
		if self.sink:
			self.sink.add(_data)


	'''
	Audio/video timestamps are computed separate.
	Return miliseconds corresponding to current timestamp.
	'''
	def stampV(self):
		if self.stampVideoNext < self.stampCurrent:
			logging.warning('Video stamp underrun %.1fmsec' % (self.stampCurrent-self.stampVideoNext) )
			self.stampVideoNext = self.stampCurrent

		self.stampCurrent= self.stampVideoNext
		self.stampVideoNext+= self.rateVideo

		return self.stampCurrent



	'''
	AAC audio block typically consist of 1024 samples, but potentially can vary.
	'''
	def stampA(self, _bytes):
		if self.stampAudioNext < self.stampCurrent:
			logging.warning('Audio stamp underrun %.1fmsec' % (self.stampCurrent-self.stampAudioNext) )
			self.stampAudioNext= self.stampCurrent

		self.stampCurrent= self.stampAudioNext
		self.stampAudioNext+= self.rateAudio *_bytes


		return self.stampCurrent



	#FLVTAG, including 4 bytes size
	def tag(self, _type, _stamp=0, _data=[b'']):
		if _stamp<0 or _stamp>0x7fffffff:
			logging.error('Stamp out of range: %.1f' % _stamp)
			_stamp= 0


		_stamp= int(_stamp).to_bytes(4, 'big')

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
		audio= 4* (audio==True)

		return b'\x46\x4c\x56\x01' +bytes([video+audio]) +b'\x00\x00\x00\x09' +b'\x00\x00\x00\x00'


	#Data tag
	def dataTag(self, _data, _stamp=0):
		tagA= self.tag(18, _stamp, [_data])

		return b''.join(tagA)


	#VIDEODATA+AVCVIDEOPACKET
	def videoTag(self, _type, _key, _data=b'', stamp=0):
		dataLen= b''
		if _type==1:
			dataLen= len(_data).to_bytes(4, 'big')


		vData= [
			  b'\x17' if _key else b'\x27'	#frame type (1=key, 2=not) and codecID (7=avc)
			, bytes([_type])				#AVCPacketType
			, b'\x00\x00\x00'				#Composition time
			, dataLen
			, _data
		]

		tagA= self.tag(9, stamp, vData)		#prepare tag for data substitution


		return b''.join(tagA)



	#AVCDecoderConfigurationRecord
	def videoDCR(self):
		nalSz= 4
		
#  todo 98 (flv) +0: Init stream with SPS and PPS provided
		sps= b'\x27\x4d\x40\x33\x9a\x64\x03\xc0\x11\x3f\x2c\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea\x60\xe8\x60\x00\xb7\x18\x00\x02\xdc\x6c\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00\x5b\x8d\x97\x79\x70\x78\x44\x22\x52\xc0'
		pps= [b'\x28\xee\x38\x80']

		headDCR= [
	   		  b'\x01'								#version
	    	, b'\x4d'								#SPS profile
	    	, b'\x40'								#SPS compatibility
	    	, b'\x33'								#SPS level
	    	, bytes([int('11111100',2) +nalSz-1])	#ff, 6xb reserved, nal-1 size
	    	, bytes([int('11100000',2) +1])			#e1, 3xb reserved, sps num
	    	, len(sps).to_bytes(2,'big')			#sps len
	    	, sps
			, bytes([ len(pps) ])
	    ]

		for cPps in pps:
			headDCR.extend([ len(cPps).to_bytes(2,'big'), cPps ])


		dcr= b''.join(headDCR)
		
		return dcr



	#AUDIODATA+AACAUDIODATA
	def audioTag(self, _type, _data=b'', stamp=0):

		aData= [
			  bytes([ (10<<4) +(3<<2) +(1<<1) +1 ])	#af: 4xb=AAC, 2xb=AACSR, 16bit, stereo
			, bytes([_type])						#AACPacketType
			, _data
		]

		tagA= self.tag(8, stamp, aData)			#prepare tag for data substitution


		return b''.join(tagA)



	#AudioSpecificConfig
	def audioSC(self):
		refDCR= b'\x11\x90\x00\x00\x00'

		return b'\x11\x90\x00\x00\x00'














'''
h264 Muxer class
Requires Sink to be specified
'''
class MuxH264(Mux):
	h264Presets= {
	  	(1080,2997,0): b'\'M@3\x9ad\x03\xc0\x11?,\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea`\xe8`\x00\xb7\x18\x00\x02\xdcl\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00[\x8d\x97ypxD"R\xc0'
		, -1: b'\x28\xee\x38\x80'
	}

	sink= None


	def __init__(self, _sink):
		self.sink= _sink

		if not self.sink:
			logging.error('Sink not specified')
			return

		self.header(self.h264Presets[(1080,2997,0)])
		self.header(self.h264Presets[-1])



	def add(self, _atom):
		if not self.sink:
			return

		if _atom.typeAVC:
			self.flush(b'\x00\x00\x00\x01' +_atom.data)



	def stop(self):
		if not self.sink:
			return

		self.sink.close()

		self.sink= None


	def header(self, _data):
		if not self.sink:
			return

		self.flush(b'\x00\x00\x00\x01' +_data)


	def flush(self, _data):
		if self.sink:
			self.sink.add(_data)






'''
AAC Muxer class
Requires Sink to be specified
'''
class MuxAAC(Mux):
	sink= None

	doADTS= True
	adts= Bits.bitsCollect([
		  (12, 0b111111111111)	#fff first 8 bits
		, (1, 0)				#version, mpeg4=0
		, (2, 0)				#layer(0)
		, (1, 1)				#no protection
		, (2, AACStatic.AOT_AAC_LC-1)	#profile-1
		, (4, 3)				#freq index, 3=48000
		, (1, 0)				#private
		, (3, 2)				#chanCFG, 2=L+R
		, (1, 0)
		, (1, 0)				#home
		, (1, 0)				#(c)
		, (1, 0)				#(c)
		, (13, 0)				#len
		, (11, 0b11111111111)	#fill
		, (2, 1-1)				#frames-1
	], True)
	adtsLen= 7


	def __init__(self, _sink, adts=True):
		self.sink= _sink

		if not self.sink:
			logging.error('Sink not specified')
			return


		self.doADTS= adts



	def add(self, _atom):
		if not self.sink:
			return

		if _atom.typeAAC:
			if len(_atom.data)>(0b1111111111111):
				logging.warning('Too big AAC found, skipped: %d' % len(_atom.data))
				return

			if self.doADTS:
				adtsHead= self.adts +(len(_atom.data)+self.adtsLen<<13)	#-13 bit pos
				self.flush(adtsHead.to_bytes(self.adtsLen, 'big'))

			self.flush(_atom.data)


	def stop(self):
		if not self.sink:
			return

		self.sink.close()

		self.sink= None


	def flush(self, _data):
		if self.sink:
			self.sink.add(_data)
			