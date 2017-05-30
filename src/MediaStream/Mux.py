class Mux():
	headerA= []



	def __init__(self, _headerA=[]):
		self.headerA= _headerA



	'''
	Produce header to be sent before data
	'''
	def header(self):
		return b''.join(self.headerA)



	def add(self, _atom):
		return _atom.data



	def stop(self):
		return







from .AAC import *
import logging


'''
FLV Muxer class
'''
class MuxFLV(Mux):
	stat= {'frames': 0, 'aac': 0}

	stampCurrent= 0.

	stampVideoNext= 0.
	rateVideo= 1000./ (30000./1001) #29.97fps frame duration
	stampAudioNext= 0
	rateAudio= 1000./ 48000

	useAudio= True



	@staticmethod
	def defaults(fps=None, srate=None):
		if fps:
			MuxFLV.rateVideo= 1000./fps
		if srate:
			MuxFLV.rateAudio= 1000./srate



	def __init__(self, _headerA, fps=None, audio=True, srate=None):
		Mux.__init__(self, _headerA)

		self.stat= {'frames': 0, 'aac': 0}

		self.stampCurrent= 0.

		self.stampVideoNext= 0.
		if fps:
			self.rateVideo= 1000./fps
		self.stampAudioNext= 0.
		if srate:
			self.rateAudio= 1000./srate


		self.useAudio= audio



	'''
	Given [SPS, PPS] array, builds FLV header.
	'''
	def header(self):
		outHeader= []

		outHeader.append( self.flvSign() )
		outHeader.append( self.videoTag(0,True,self.videoDCR(self.headerA[0], self.headerA[1:])) )
		outHeader.append( self.audioTag(0,self.audioSC()) )

		return b''.join(outHeader)



	def add(self, _atom):
		if _atom.typeAVC and _atom.AVCVisible:
			self.stat['frames']+= 1
			
			return self.videoTag(1, _atom.AVCKey, _atom.data, self.stampV())
			

		if self.useAudio and _atom.typeAAC:
			if len(_atom.data)>2040:
				logging.warning('Too big AAC found, skipped: %d' % len(_atom.data))
				return

			self.stat['aac']+= 1
			
			return self.audioTag(1, _atom.data, self.stampA(_atom.AACSamples))



	def stop(self):
		logging.info('%d frames, %d aac' % (self.stat['frames'], self.stat['aac']))

		return self.videoTag(2,True,stamp=self.stampV())



### PRIVATE



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
	def flvSign(self, video=True, audio=True):
		video= 1* (video==True)
		audio= 4* (audio==True)

		return b'FLV\x01' +bytes([video+audio]) +b'\x00\x00\x00\x09' +b'\x00\x00\x00\x00'



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
	def videoDCR(self, _sps, _pps):
		nalSz= 4
		
		headDCR= [
	   		  b'\x01'								#version
	    	, b'\x4d'								#SPS profile
	    	, b'\x40'								#SPS compatibility
	    	, b'\x33'								#SPS level
	    	, bytes([int('11111100',2) +nalSz-1])	#ff, 6xb reserved, nal-1 size
	    	, bytes([int('11100000',2) +1])			#e1, 3xb reserved, sps num
	    	, len(_sps).to_bytes(2,'big')			#sps len
	    	, _sps
			, bytes([ len(_pps) ])
	    ]

		for cPps in _pps:
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

		return refDCR














'''
h264 Muxer class
'''
class MuxH264(Mux):
	def __init__(self, _headerA):
		Mux.__init__(self, _headerA)



	def header(self):
		outHeader= []
		for cData in self.headerA:
			outHeader.append(b'\x00\x00\x00\x01' +cData)

		return b''.join(outHeader)



	def add(self, _atom):
		if _atom.typeAVC:
			return (b'\x00\x00\x00\x01' +_atom.data)








'''
AAC Muxer class
'''
class MuxAAC(Mux):
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


	def __init__(self, _headerA, adts=True):
		Mux.__init__(self, _headerA)

		self.doADTS= adts



	def add(self, _atom):
		if _atom.typeAAC:
			if len(_atom.data)>(0b1111111111111):
				logging.warning('Too big AAC found, skipped: %d' % len(_atom.data))
				return

			if self.doADTS:
				adtsHead= self.adts +(len(_atom.data)+self.adtsLen<<13)	#-13 bit pos
				return adtsHead.to_bytes(self.adtsLen, 'big') +_atom.data

			return _atom.data
