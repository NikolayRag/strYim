from MediaStream.AAC import *
import logging


'''
Support class to detect Yi4k (only) AAC blocks looking pretty suitable
It should be completely replaced by native AAC decoder. Eventually.

Yi4k's .mp4 stream has [h264,AAC,...] structure, where AAC is 0 to 2 blocks.
That is because one AAC block duration is always 21.(3)ms (1024/48000),
 and frame duration for slowest FPS is 41.(6)ms (1/24fps). So AAC underflow
 periodically and placed twice to prevent lag.

AAC must be separately provided to FLV muxer to apply individual timestamps,
 and since AAC format doesn't have easy-to-detect signatures, it's neccessary
 to to detect correct boundaries of provided bytearray.
MediaStream.AACCore is used here as an incomplete, though acceptable
 AAC detector.


'''
class AACDetect():
	#Allowed max_sfb, Yi4k specific.
	#Such strange form is used to compare current sfb
	#to 8-seq and 'started' state.
	sfb8= [[12], [12]]
	sfb1= [[0,40], [40]]

	started= False
	seqNow= False

	def __init__(self):
		self.reset()


	'''
	Tell than new context(.mp4 file) will follow.
	'''
	def reset(self):
		self.started= False
		self.seqNow= False


	'''
	Provided with seamless AAC binary, detect if it should be splitted.
	'''
	def detect(self, _data, _limit=2):
		aacStartA= []
		aacPos= -1

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
				logging.info('AAC started from mid')

			aacStartA.append(aacPos)

			self.seqNow= seqAfter
			self.started= True




		aacEndA= aacStartA[1:] +[len(_data)]

		aacA= []	#[[start,end],..] pairs
		for aacStart,aacEnd in zip(aacStartA,aacEndA):
			aacA.append([aacStart,aacEnd])

		return aacA
		