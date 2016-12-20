import subprocess, tempfile, re

from .byteTransit import *
from .mp4Atom import *
from .kiLog import *



class Mp4Recover():
	h264Presets= {
		  (1080,30,0): b'\'M@3\x9ad\x03\xc0\x11?,\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea`\xe8`\x00\xb7\x18\x00\x02\xdcl\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00[\x8d\x97ypxD"R\xc0'
		, -1: b'\x28\xee\x38\x80'
	}

	signMoov= b'\x6d\x6f\x6f\x76'
	signAAC= b'\x21'
	signAVC= [b'\x25\xb8\x01\x00', b'\x21\xe0\x10\x11', b'\x21\xe0\x20\x21', b'\x21\xe0\x30\x31', b'\x21\xe0\x40\x41', b'\x21\xe0\x50\x51', b'\x21\xe0\x60\x61', b'\x21\xe0\x70\x71']

	transit= None
	atomCB= None


	def __init__(self, _atomCB):
		self.transit= byteTransit(self.atomsFromRaw, 500000)


		self.atomCB= _atomCB

		if callable(self.atomCB):
			self.atomCB( Atom(data=self.h264Presets[(1080,30,0)]).setAVC(True,False) )
			self.atomCB( Atom(data=self.h264Presets[-1]).setAVC(True,False) )
		

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
	def atomsFromRaw(self, _data, _finalize=False):
		recoverMatchesA= self.analyzeMp4(_data, _finalize)


		dataCosumed= 0
		for match in recoverMatchesA:
			match.bindData(_data)
			self.atomCB(match)

			dataCosumed= match.outPos


		return dataCosumed





	'''
	Search .mp4 bytes for 264 and aac frames.
	Return Atom() array.
	
	First frame searched is IDR (Key frame).
	Last frame is the one before last found IDR frame, or before MOOV atom if found.

	If called subsequently on growing stream, 2nd and next call's data[0] will point to IDR.
	'''
	def analyzeMp4(self, _data, _finalize=False):
		signI= 0
		signI1= 1 #cached version

		KFrameLast= 0	#Last IDR frame to cut out if not finalize
		matchesA= []

		foundFalse= 0
		foundStart= 0
		while True:
			atomMatch= self.analyzeAtom(_data, foundStart, self.signAVC[signI], self.signAVC[signI1])
			if atomMatch==None: #not enough data, stop
				break

			if atomMatch==False: #retry further
				foundFalse+= 1

				foundStart= _data.find(self.signAVC[signI], foundStart+1+4)-4	#rewind to actual start
				if foundStart<0:	#dried while in search
					break

				continue


			#Atom found
			if atomMatch.typeMoov:	#abort limiting
				KFrameLast= None
				break


			matchesA.append(atomMatch)

			foundStart=	atomMatch.outPos	#shortcut for next


			if atomMatch.typeAVC:
				signI= signI1

				signI1+= 1
				if signI1==len(self.signAVC):
					signI1= 0


				if atomMatch.AVCKey:	#limits to keyframes
					KFrameLast= len(matchesA)-1



		if _finalize:
			KFrameLast= None

		atomBlock= matchesA[:KFrameLast]
		
		
		if len(atomBlock):
			kiLog.verb('%d atoms found%s' % (len(atomBlock), ', finaly' if not KFrameLast else ''))
		if foundFalse:
			if KFrameLast:
				kiLog.warn('%d false atoms in %d bytes' % (foundFalse, len(_data)))
			else:
				kiLog.verb('%d false atoms in %d bytes' % (foundFalse, len(_data)))


		return atomBlock





	'''
	Detects Atom assumed to be started from _in.
	Return: Atom if detected, False if not, or None if insufficient data.
	_in must be not less than 4.
	
	AVC: 4b:size, size:(signAVC[x],...), signAAC|(4b,signAVC[x+1])|(4b,signMoov)
	AAC: signAAC, ?:..., (4b,signAVC[x+1])|(4b,signMoov)
	MOOV: 4b:size, signMoov
	'''
	def analyzeAtom(self, _data, _inPos, _signAVC, _signAVC1):
		if (_inPos+8)>len(_data):	#too short for anything
			return None


		#AVC/MOOV
		signThis= _data[_inPos+4:_inPos+8]
		outPos= _inPos +4 +int.from_bytes(_data[_inPos:_inPos+4], 'big')


		if signThis==self.signMoov:
			if outPos>len(_data): #Not enough data to test
				return None

			return Atom(_inPos,outPos).setMOOV()


		if signThis==_signAVC:
			if (outPos+8)>len(_data): #Not enough data to test
				return None

			signNext= _data[outPos+4:outPos+8]
			if (
				   signNext!=_signAVC1
				and signNext!=self.signMoov
				and _data[outPos]!=self.signAAC[0]
			):
				return False

			return Atom(_inPos+4,outPos).setAVC(signThis==self.signAVC[0])


		#AAC
		if _data[_inPos]==self.signAAC[0]:
			outPos= _data.find(_signAVC, _inPos)-4


			moovStop= outPos
			if outPos<0:
				moovStop= len(_data)

			moovPos= _data[_inPos:moovStop].find(self.signMoov)
			if moovPos>=0:	#MOOV found ahead
				outPos= _inPos+moovPos-4


			if outPos<0:	#still nothing found
				return None

			return Atom(_inPos,outPos).setAAC()


		return False
