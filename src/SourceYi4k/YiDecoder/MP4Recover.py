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

	transit= None
	atomCB= None


	detectHelper= None


	'''
	Provide Atom() consuming callback to be fired when collected raw data
	 added by add() is sufficient to detect something.
	'''
	def __init__(self, _atomCB):
		self.detectHelper= AACDetect()
	
		self.transit= ByteTransit(self.atomsFromRaw, 500000)


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
		#Data sent to ByteTransit is cached and dispatched to .atomsFromRaw()
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
	def atomsFromRaw(self, _data, _finalize=False):
		recoverMatchesA= self.analyzeMp4(_data, _finalize)


		dataCosumed= 0
		for match in recoverMatchesA:
			match.bindData(_data)
			self.atomCB and self.atomCB(match)

			dataCosumed= match.outPos


		return dataCosumed





	'''
	Search .mp4 bytes for 264 and AAC frames.
	Return [Atom(),..] array.
	
	First frame searched is IDR (Key frame).
	Last frame is the one before last IDR frame or MOOV atom found.

	If called subsequently on growing stream,
	 2nd and next call's data[0] will surely point to IDR.
	'''
	def analyzeMp4(self, _data, _finalize=False):
		signI= 0
		signI1= 1 #cached version

		KFrameLast= 0	#Last IDR frame to cut out if not finalize
		matchesA= []

		foundFalse= 0
		foundStart= 0
		while True:
			atomMatchA= self.analyzeAtom(_data, foundStart, self.signAVC[signI], self.signAVC[signI1])
			if atomMatchA==None: #not enough data, stop
				break

			if atomMatchA==False: #retry further
				foundFalse+= 1

				foundStart= _data.find(self.signAVC[signI], foundStart+1+4)-4	#rewind to actual start
				if foundStart<0:	#dried while in search
					break

				continue


			#Atom found
			for atomMatch in atomMatchA:
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

			if KFrameLast== None:	#MOOV was detected
				break



		if _finalize:
			KFrameLast= None

			self.detectHelper.reset()


		atomBlock= matchesA[:KFrameLast]
		
		
		if len(atomBlock):
			logging.debug('%d atoms found%s' % (len(atomBlock), ', finaly' if not KFrameLast else ''))
		if foundFalse:
			if KFrameLast:
				logging.warning('%d false atoms in %d bytes' % (foundFalse, len(_data)))
			else:
				logging.debug('%d false atoms in %d bytes' % (foundFalse, len(_data)))


		return atomBlock





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
			if outPos>len(_data): #Not enough data to test
				return None

			return [Atom(_inPos,outPos).setMOOV()]


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

			return [Atom(_inPos+4,outPos).setAVC(signThis==self.signAVC[0])]


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


			AACA= []
			for aac in self.detectHelper.detect(_data[_inPos:outPos]):
				AACA.append(Atom(_inPos+aac[0],_inPos+aac[1]).setAAC())

			if len(AACA):
				return AACA


			logging.warning('AAC data should be phased out by accident')

			#fallback if all AACs are "bad".
			return [Atom(_inPos,outPos).setAAC()]


		return False
