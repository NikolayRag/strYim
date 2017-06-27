# =todo 311 (Yi, recover) +2: fix lost frames at end block
from .ByteTransit import *
from .YiAAC import *
from MediaStream import Atom
import logging




'''
MP4 recovery class, dedicated to Yi4k.
Expected MP4 characteristics, similar to any resolution/rate with
 firmware v1.3.3:
- Keyframe is every 8 frames (IDR), followed by 7 (P) frames,
- all data between frames is AAC, if any,
- AAC is allways (AOT_AAC_LC, stereo, 48k) profile
  and (CPE, id=0, common_window=1) properties
- maximum 2 AAC blocks stored seamlessly
'''
class Mp4Recover():
	#these prefixes only guaranteed with Yi4k .mp4
	signMoov= b'\x6d\x6f\x6f\x76'
	signAAC= b'\x21'
	signAVC= [b'\x25\xb8\x01\x00', b'\x21\xe0\x10\x11', b'\x21\xe0\x20\x21', b'\x21\xe0\x30\x31', b'\x21\xe0\x40\x41', b'\x21\xe0\x50\x51', b'\x21\xe0\x60\x61', b'\x21\xe0\x70\x71']
	signI= 0 #start over with

	transit= None
	atomCB= None


	detectHelper= None

	matches= 0
	matchesF= 0


	'''
	Provide Atom() consuming callback to be fired when collected raw data
	 added by add() is sufficient to detect something.
	'''
	def __init__(self, _atomCB):
		self.detectHelper= AACDetect()
	
		self.transit= ByteTransit(self.analyzeMp4)

		self.atomCB= callable(_atomCB) and _atomCB



	'''
	Add chunks of raw .mp4 binary data from camera.
	Data can be delivered sequentally in chunks splitted any way.

		_ctx
			Context, switching it to any new value indicates
			.mp4 file boundary, so all previous data collected
			 must be consumed.
	'''
	def add(self, _data, _ctx=None):
		#Data sent to ByteTransit is cached and dispatched to .analyzeMp4()
		self.transit.add(_data, _ctx)




	'''
	Parse binary .mp4 data for h264/AAC atoms.
	Called by ByteTransit after it got anough data by .add().
	Return number of bytes actually consumed, suitable for ByteTransit.

		data
			.mp4 byte stream data

		finalize
			boolean, indicates no more data for this context will be sent (if consumed all).
	'''
	def analyzeMp4(self, _data, _finalize=False):
		matchesBefore= self.matches

		nextStart= 0
		while True:
			atomMatch= self.findAtom(_data, nextStart)
			
			if not atomMatch:
				break
			
			if atomMatch.typeMoov:
				logging.info('MOOV')
				
				_finalize= True
				break


			nextStart= atomMatch.outPos	#shortcut for next


			if atomMatch.typeAAC:
				thisStart= atomMatch.inPos

				splitAACA= self.detectHelper.detect(_data[thisStart:nextStart])
				if len(splitAACA):
					for aac in splitAACA:
						self.pushAtom(Atom(thisStart+aac[0],thisStart+aac[1]).setAAC(), _data)
				
				else:
					logging.warning('AAC data should be phased out by accident')

					self.pushAtom(atomMatch, _data)


			if atomMatch.typeAVC:
				self.pushAtom(atomMatch, _data)
				self.matchesF+= 1


		if matchesBefore:
			logging.debug('%d atoms found' % matchesBefore)


		if _finalize:
			logging.info('Total %d atoms found, %d frames' % (self.matches, self.matchesF))
			self.matches= 0
			self.matchesF= 0


			self.detectHelper.reset()
		
			self.signI= 0


		return nextStart



	'''
	Pass Atom with data to defined callback
	'''
	def pushAtom(self, _atom, _data):
		self.matches+= 1

		_atom.bindData(_data)
		self.atomCB and self.atomCB(_atom)



	'''
	Find first Atom of desired signature from specified position
	'''
	def findAtom(self, _data, _start):
		signI1= self.signI +1
		if signI1==len(self.signAVC):
			signI1= 0


		while True:
			atomMatch= self.analyzeAtom(_data, _start, self.signAVC[self.signI], self.signAVC[signI1])

			if atomMatch==None: #not enough data, stop
				return

			if atomMatch==False: #retry further
				logging.debug('false atoms in %d bytes' % (len(_data)))

				_start= _data.find(self.signAVC[self.signI], _start+1+4)-4	#rewind to actual start
				if _start<0:	#dried while in search
					return

			if atomMatch:
				if atomMatch.typeAVC:
					self.signI= signI1

				return atomMatch



	'''
	Detects Atom assumed to be started from _inPos.
	
	AVC: 4b:size, size:(signAVC[x],...), signAAC|(4b,signAVC[x+1])|(4b,signMoov)
	AAC: signAAC, ?:..., (4b,signAVC[x+1])|(4b,signMoov)
	MOOV: 4b:size, signMoov

	Return: Atom if detected, False if not, or None if insufficient data.

		_signAVC
			Bytes prefix to find 'current' frame of interest,
			cycled on successfully AVC detection.

		_signAVC1
			Bytes prefix of 'next after current' frame.
	'''
	def analyzeAtom(self, _data, _inPos, _signAVC, _signAVC1):
		if (_inPos+8)>len(_data):	#too short for anything
			return None


		#AVC/MOOV
		signThis= _data[_inPos+4:_inPos+8]
		outPos= _inPos +4 +int.from_bytes(_data[_inPos:_inPos+4], 'big')


		if signThis==self.signMoov:
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


		#AAC, as all between-frame data assumed to be
#  todo 180 (feature, aac) +0: detect AAC length by native decoding
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
