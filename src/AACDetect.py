from .AACCore import *
from .kiLog import *


'''
Support class to detect Yi4k (only) AAC blocks looking pretty suitable
It should be completely replaced by native AAC decoder. Eventually.
'''
class AACDetect():
	#allowed max_sfb for [started]
	sfb8= [[12], [12]]
	sfb1= [[0,40], [40]]

	started= False
	seqNow= False

	def __init__(self):
		self.reset()


	def reset(self):
		self.started= False
		self.seqNow= False


	def detect(self, _data, _limit=2):
		aacStartA= []
		aacPos= -1

			#spike. Yi4k limit, 30fps assumes mid-frame data have maximum 2 AACs
		while (True if not _limit else (len(aacStartA)<_limit)):
			aacPos= _data.find(b'\x21', aacPos+1)
			if aacPos==-1:
				break

			if (
				(aacPos>0 and aacPos<256)	#limit from begin
				or (len(_data)-aacPos<256)	#limit from end
			):
				continue



			aac= AACCore().aac_decode_frame(_data[aacPos:], limitSequence=self.seqNow)
			seqAfter= (	#is aac ended up into sequence
				aac.ics0.windows_sequence0==AACStatic.LONG_START_SEQUENCE
				or aac.ics0.windows_sequence0==AACStatic.EIGHT_SHORT_SEQUENCE
			)

			if (
				aac.error
				#Yi4k specific:
				or (aac.ics0.max_sfb not in [self.sfb1,self.sfb8][aac.ics0.windows_sequence0==AACStatic.EIGHT_SHORT_SEQUENCE][self.started]) #allowed Maxsfb
				or (aac.ics0.use_kb_window0 == seqAfter)	#limit combinations
			):
				continue

			if not self.started and not aac.ics0.max_sfb:
				kiLog.warn('AAC started from mid')

			aacStartA.append(aacPos)

			self.seqNow= seqAfter
			self.started= True




		aacEndA= aacStartA[1:] +[len(_data)]

		aacA= []	#[[start,end],..] pairs
		for aacStart,aacEnd in zip(aacStartA,aacEndA):
			aacA.append([aacStart,aacEnd])

		return aacA
		