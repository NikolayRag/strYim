'''
Construct/restore network chunk for transfer from Yi.
'''
class YiData():
	import json
	global json


	meta= b''
	metaRemain= 0
	binaryRemain= 0

	restoreCB= None



	@staticmethod
	def build(_binary, _ctx):
		if not _binary:
			_binary= b''

		meta= b'%3d%10d' % (_ctx, len(_binary))
		return [meta, _binary]



	def __init__(self, _cb=None):
		self.restoreCB= _cb

		self.reset()



	'''
	Pass raw data from socket to .restore() to collect built data.
	'''
	def restore(self, _data):
		if not _data or not callable(self.restoreCB):
			return


		dataPos= 0
		
		if self.metaRemain:
			dataPos= min(self.metaRemain, len(_data))
			self.meta+= _data[:dataPos]

			self.metaRemain-= dataPos


			if not self.metaRemain:
				self.dataRemain= int(self.meta[3:])

				self.restoreCB(self.meta)


		if self.dataRemain:
			dataAvail= min(self.dataRemain, max(len(_data)-dataPos,0) )
			self.dataRemain-= dataAvail

			if not self.dataRemain:
				self.reset()




	def reset(self):
		self.meta= b''
		self.metaRemain= 13 #refer meta mask
