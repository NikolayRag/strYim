'''
Data wrapper for send/recieve data.
Provide binary data to build() to create header,
Provede [header,data,...] stream to restore() to split binary data back
 into original blocks.
'''
class YiData():
	import json
	global json


	meta= b''
	metaRemain= 0
	binaryRemain= 0
	dataPos= 0

	metaCB= None
	dataCB= None



	@staticmethod
	def build(_binary, _ctx):
		if not _binary:
			_binary= b''

		meta= b'%3d%10d' % (_ctx, len(_binary))
		return meta



	def __init__(self, _metaCB=None, _dataCB=None):
		self.metaCB= _metaCB
		self.dataCB= _dataCB

		self.reset()



	'''
	Pass raw data from socket to .restore() to collect built data.
	'''
	def restore(self, _data):
		if not _data:
			return

		while self.dataPos<len(_data):
			self.pickMeta(_data)
			self.pickData(_data)

		self.dataPos= 0



	def pickMeta(self, _data):
		if not self.metaRemain:
			return

		#read
		cAmt= min(self.metaRemain, len(_data)-self.dataPos )

		dataPosFrom= self.dataPos
		self.dataPos+= cAmt
		self.metaRemain-= cAmt

		self.meta+= _data[dataPosFrom:self.dataPos]

		if not self.metaRemain:
			self.dataRemain= int(self.meta[3:])

			callable(self.metaCB) and self.metaCB(self.meta)



	def pickData(self, _data):
		if not self.dataRemain:
			return

		cAmt= min(self.dataRemain, len(_data)-self.dataPos )

		dataPosFrom= self.dataPos
		self.dataPos+= cAmt
		self.dataRemain-= cAmt

		callable(self.dataCB) and self.dataCB(_data[dataPosFrom:self.dataPos])
	
		if not self.dataRemain:
			self.reset()



	def reset(self):
		self.meta= b''
		self.metaRemain= 13 #refer meta mask
		self.dataRemain= 0
