from .AACCore import *


'''
Support class to detect Yi4k (only) AAC blocks looking pretty suitable
It should be completely replaced by native AAC decoder. Eventually.
'''
class AACDetect():
	#allowed max_sfb's
	sfb8= 12
	sfb1= [0,40]

	started= False
	seqNow= False

	def __init__(self):
		self.reset()


	def reset(self):
		self.started= False
		self.seqNow= False


	def detect(self, _data):
		aacStartA= []
		aacPos= -1

		while True:
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
				aac.sce_ics0.windows_sequence[0]==1
				or aac.sce_ics0.windows_sequence[0]==2
			)

			if (
				aac.error
				#Yi4k specific:
				or (aac.sce_ics0.max_sfb!= (self.sfb8 if aac.sce_ics0.is8 else self.sfb1[self.started])) #predefined Maxsfb
				or (self.started and not aac.ac_che.ms_present) #non-first must be masked
				or (aac.sce_ics0.use_kb_window[0] == seqAfter)	#limit combinations
			):
				continue


			aacStartA.append(aacPos)

			self.seqNow= seqAfter
			self.started= True


		aacEndA= aacStartA[1:] +[len(_data)]

		aacA= []	#[[start,end],..] pairs
		for aacStart,aacEnd in zip(aacStartA,aacEndA):
			aacA.append([aacStart,aacEnd])

		return aacA