from .kiLog import *

'''
FLV Muxer class
Requires Sink to be specified
'''
class MuxFLV():
	stampVideo= 0.
	rateVideo= 1000./ (30000./1001) #29.97
	stampAudio= 0
	rateAudio= 1000./16000

	useAudio= True

	sink= None


	@staticmethod
	def defaults(fps=None, bps=None):
		if fps:
			MuxFLV.rateVideo= 1000./fps
		if bps:
			MuxFLV.rateAudio= 1000./bps


	def __init__(self, _sink, fps=None, audio=True, bps=None):
		self.stampVideo= 0.
		if fps:
			self.rateVideo= 1000./fps
		self.stampAudio= 0.
		if bps:
			self.rateAudio= 1000./bps

		self.sink= _sink

		if not self.sink:
			return


		self.useAudio= audio

		self.sink.add( self.header(audio=self.useAudio) )
		self.sink.add( self.dataTag(self.flvMeta(self.useAudio)) )
		self.sink.add( self.videoTag(0,True,self.videoDCR()) )
		self.sink.add( self.audioTag(0,self.audioSC()) )


	def add(self, _atom):
		if not self.sink:
			return

		if _atom.typeAVC:
			flvTag= self.videoTag(1, _atom.AVCKey, _atom.data, self.stampV())
			self.sink.add(flvTag)

		if self.useAudio and _atom.typeAAC:
			if len(_atom.data)>2040:
				kiLog.warn('Too big AAC found, skipped: %d' % len(_atom.data))
				return

			flvTag= self.audioTag(1, _atom.data, self.stampA( len(_atom.data) ))
			self.sink.add(flvTag)


	def stop(self):
		if not self.sink:
			return

		self.sink.add( self.videoTag(2,True,stamp=self.stampV()) )
		self.sink.close()

		self.sink= None



	#private

	'''
	Return miliseconds corresponding to current timestamp, incrementing by one for virtually same stamp.
	'''
	def stampV(self):
#		if self.stampVideo < self.stampAudio:
#			kiLog.warn('Video stamp underrun %dsec' % (self.stampAudio-self.stampVideo))
#			self.stampVideo= self.stampAudio

		stampOut= self.stampVideo
		self.stampVideo+= self.rateVideo

		return int(stampOut)

# -todo 117 (mux, flv, bytes, aac) +2: reveal actual AAC frame length
	def stampA(self, _bytes):
#		if self.stampAudio < self.stampVideo:
#			kiLog.warn('Audio stamp underrun %dsec' % (self.stampVideo-self.stampAudio))
#			self.stampAudio= self.stampVideo


		stampOut= self.stampAudio
		self.stampAudio+= self.rateAudio *_bytes

		return int(stampOut)


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
		
# -todo 98 (flv) +0: build SPS and PPS
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



# -todo 90 (flv) +0: construct META
	def flvMeta(self, audio=True):
		headMetaV= b'\x02\x00\nonMetaData\x08\x00\x00\x00\x0b\x00\x08duration\x00@D=\x91hr\xb0!\x00\x05width\x00@\x9e\x00\x00\x00\x00\x00\x00\x00\x06height\x00@\x90\xe0\x00\x00\x00\x00\x00\x00\rvideodatarate\x00@\xc7\x00\xcd\xe0\x00\x00\x00\x00\tframerate\x00@=\xf6\xff\x825\xd3D\x00\x0cvideocodecid\x00@\x1c\x00\x00\x00\x00\x00\x00\x00\x0bmajor_brand\x02\x00\x04isom\x00\rminor_version\x02\x00\x03512\x00\x11compatible_brands\x02\x00\x10isomiso2avc1mp41\x00\x07encoder\x02\x00\rLavf57.57.100\x00\x08filesize\x00A\x8d5\x11\x10\x00\x00\x00\x00\x00\t'
		headMetaAV= b'\x02\x00\nonMetaData\x08\x00\x00\x00\x10\x00\x08duration\x00@N\x07\xae\x14z\xe1H\x00\x05width\x00@\x9e\x00\x00\x00\x00\x00\x00\x00\x06height\x00@\x90\xe0\x00\x00\x00\x00\x00\x00\nvideodatarate\x00@\xc6\xfc\x17@\x00\x00\x00\x00\tframerate\x00@=\xf8S\xe2Uk(\x00\x0cvideocodecid\x00@\x1c\x00\x00\x00\x00\x00\x00\x00\naudiodatarate\x00@_?\xa0\x00\x00\x00\x00\x00\x0faudiosamplerate\x00@\xe7p\x00\x00\x00\x00\x00\x00\x0faudiosamplesize\x00@0\x00\x00\x00\x00\x00\x00\x00\x06stereo\x01\x01\x00\x0caudiocodecid\x00@$\x00\x00\x00\x00\x00\x00\x00\x0bmajor_brand\x02\x00\x04avc1\x00\nminor_version\x02\x00\x010\x00\x11compatible_brands\x02\x00\x08avc1isom\x00\x07encoder\x02\x00\nLavf57.41.100\x00\x08filesize\x00A\x95\xd1\x9fx\x00\x00\x00\x00\x00\t'

		if audio:
			return headMetaAV

		return headMetaV













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

		if _atom.typeAVC:
			self.sink.add(b'\x00\x00\x00\x01' +_atom.data)


	def stop(self):
		if not self.sink:
			return

		self.sink.close()

		self.sink= None











'''
AAC test Muxer class
Requires Sink to be specified
'''
class MuxAAC():

	sink= None

	doADTS= True

	def __init__(self, _sink, adts=True):
		self.sink= _sink

		if not self.sink:
			kiLog.err('Sink not specified')
			return


		self.doADTS= adts



	def add(self, _atom):
		if not self.sink:
			return

		if _atom.typeAAC:
			if len(_atom.data)>2040:
				kiLog.warn('Too big AAC found, skipped: %d' % len(_atom.data))
				return



#  todo 108 (aac) +0: write (optional) ADTS header
			'''
A 	12 	syncword 0xFFF, all bits must be 1
B 	1 	MPEG Version: 0 for MPEG-4, 1 for MPEG-2
C 	2 	Layer: always 0
D 	1 	protection absent, Warning, set to 1 if there is no CRC and 0 if there is CRC
E 	2 	profile, the MPEG-4 Audio Object Type minus 1
F 	4 	MPEG-4 Sampling Frequency Index (15 is forbidden)
G 	1 	private bit, guaranteed never to be used by MPEG, set to 0 when encoding, ignore when decoding
H 	3 	MPEG-4 Channel Configuration (in the case of 0, the channel configuration is sent via an inband PCE)
I 	1 	originality, set to 0 when encoding, ignore when decoding
J 	1 	home, set to 0 when encoding, ignore when decoding
K 	1 	copyrighted id bit, the next bit of a centrally registered copyright identifier, set to 0 when encoding, ignore when decoding
L 	1 	copyright id start, signals that this frame's copyright id bit is the first bit of the copyright id, set to 0 when encoding, ignore when decoding
M 	13 	frame length, this value must include 7 or 9 bytes of header length: FrameLength = (ProtectionAbsent == 1 ? 7 : 9) + size(AACFrame)
O 	11 	Buffer fullness
P 	2 	Number of AAC frames (RDBs) in ADTS frame minus 1, for maximum compatibility always use 1 AAC frame per ADTS frame
Q 	16 	CRC if protection absent is 0 
			'''

		

			if self.doADTS:
				adts= b'\xff\xf1\x4c\x80' +(len(_atom.data)*32+255).to_bytes(2,'big') +b'\xfc'
				self.sink.add(adts +_atom.data)
			else:
				self.sink.add(_atom.data)


	def stop(self):
		if not self.sink:
			return

		self.sink.close()

		self.sink= None


