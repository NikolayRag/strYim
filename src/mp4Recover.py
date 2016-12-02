import subprocess, tempfile, re

from .byteTransit import *
from .kiLog import *


class Atom():
# -todo 124 (recover, mp4) +0: change Atom fields to data plus atom-specific structures
	type= None
	data= None

	def __init__(self, _type=None, _data=b''):
		self.type= _type
		self.data= _data



# =todo 101 (recover) +2: use native atoms searching: [h264, aac, ...]
class Mp4Recover():
	h264Presets= {
		  (1080,30,0): b'\'M@3\x9ad\x03\xc0\x11?,\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea`\xe8`\x00\xb7\x18\x00\x02\xdcl\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00[\x8d\x97ypxD"R\xc0'
		, -1: b'\x28\xee\x38\x80'
	}


	transit= None
	atomCB= 	None


	def __init__(self, _atomCB):
		self.transit= byteTransit(self.atomsFromRaw, 500000)


		self.atomCB= _atomCB

		if callable(self.atomCB):
			self.atomCB( Atom('IDR', self.h264Presets[(1080,30,0)]) )
			self.atomCB( Atom('IDR', self.h264Presets[-1]) )
		

	def add(self, _data, _ctx=None):
		self.transit.add(_data, _ctx)




	'''
	Provide raw mp4 data to parse in addition to allready provided.
	Return numer of bytes actually consumed.

		data
			.mp4 byte stream data

		finalize
			boolean, indicates no more data for this context will be sent (if consumed all).
	'''
# -todo 123 (clean) +0: remove ctx arg
	def atomsFromRaw(self, _data, _ctx, _finalize=False):
		recoverMatchesA= self.analyzeMp4(_data)


		kiLog.ok("%d matches" % len(recoverMatchesA))


		dataCosumed= 0
		for match in recoverMatchesA:
			restoredData= _data[ match['offset'] : match['len'] ]
			self.atomCB( Atom(match['type'],restoredData) )

			dataCosumed= match['offset'] +match['len']


		return dataCosumed



	'''
	Search .mp4 bytes for 264 and aac frames.
	Return Atom() array.
	
	First frame searched is IDR (Key frame).
	Last frame is the one before last found IDR frame, or before MOOV atom if found.

	If called subsequently on growing stream, 2nd and next call's data[0] will point to IDR.
	'''
	def analyzeMp4(self, _data):
		signMoov= b'\x6d\x6f\x6f\x76'
		signAAC= b'21' #aac
		signA= [b'\x25\xb8\x01\x00', b'\x21\xe0\x10\x11', b'\x21\xe0\x20\x21', b'\x21\xe0\x30\x31', b'\x21\xe0\x40\x41', b'\x21\xe0\x50\x51', b'\x21\xe0\x60\x61', b'\x21\xe0\x70\x71']
		signI= 0

		foundBegin= 3 #will start at 4, to allow [0:4] bytes be frame size
		lastKFrame= None	#Last IDR frame to cut out if not finalize
		matchesA= []
		'''
		search: Key AVC, [AVC|AAC|MOOV], ...
		'''
		while True:
			#AVC frame first, should end up with AAC or MOOV
			foundBegin= _data.find(signA[signI], foundBegin+1)
			if foundBegin==-1:
				break

			foundLen= int.from_bytes(_data[foundBegin-4:foundBegin], 'big')
			foundEnd= foundBegin+foundLen
			if foundEnd>len(_data): #false positive
				continue


			nextSignI= signI +1
			if nextSignI==len(signA):
				nextSignI= 0


			assumeAACNext= _data[foundEnd]==signAAC
			if not assumeAACNext:	#assumed not AAC found, must be AVC|MOOV then
				if (
					_data[foundEnd+4:foundEnd+8]!=signA[nextSignI]
					and _data[foundEnd+4:foundEnd+8]!= signMoov
				):
					continue	#false positive


			#AVC was found

			matchesA.append({'in':foundBegin, 'out':foundEnd, 'type':'IDR' if not signA else 'P'})


			#last frame and remaining should be left to next run untill it's not final
#			if not _finalize and mp4Match['type']=='IDR':
#				self.safePos= mp4Match['offset']
#				lastKFrame= len(matchesA)





		return matchesA[:lastKFrame]








import sublime, sublime_plugin

class YiTestCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		f= open('e:/yi/L0010840.MP4', 'rb')
		b= f.read()
		f.close()

		print( Mp4Recover(None).analyzeMp4(b) )
