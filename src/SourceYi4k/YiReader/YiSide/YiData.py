import logging



'''
Data wrapper for send/recieve data.
Provide binary data to build() to create header,
Provede [header,data,...] stream to restore() to split binary data back
 into original blocks.
'''
class YiData():
	import json
	global json

	#message type constants
	NONE= 0
	DATA= 1
	OVERFLOW= 2
	STOP= 3

	metaLength= 16
	meta= b''
	metaRemain= 0
	binaryRemain= 0
	dataPos= 0

	dataCB= None
	ctxCB= None
	stateCB= None



	'''
	Create header out os data provided, to be sent prior that data.
	'''
	@staticmethod
	def message(_type=None, _data=None):
		_type= _type or YiData.NONE
		msgBody= b' ' *15

		if _type==YiData.NONE:
			None

		elif _type==YiData.DATA:
			if not _data:
				_data= [0, b'']
			msgBody= b'%4d%11d' % (_data[0], len(_data[1]))

		elif _type==YiData.OVERFLOW:
			msgBody= (b' '*4) +(b'%11d' % _data)

		elif _type==YiData.STOP:
			None


		meta= (b'%1d' % _type) +msgBody
		return meta





	def __init__(self, _dataCB=None, _ctxCB=None, _stateCB=None):
		self.dataCB= callable(_dataCB) and _dataCB
		self.ctxCB= callable(_ctxCB) and _ctxCB
		self.stateCB= callable(_stateCB) and _stateCB

		self.reset()



	'''
	Pass raw [header,data,...] from socket to collect orignal data chunks.
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
			hType= int(self.meta[:1])

			if hType==YiData.DATA:
				hCtx= int(self.meta[1:5])
				self.dataRemain= int(self.meta[5:])

				logging.debug('Data in: ctx %d, len %d' % (hCtx, self.dataRemain))

				self.ctxCB and self.ctxCB({'ctx':hCtx, 'len':self.dataRemain})

			elif hType!=YiData.NONE:
				logging.debug('State message: %d' % hType)
				
				self.stateCB and self.stateCB(hType, self.meta[1:])



	def pickData(self, _data):
		if not self.dataRemain:
			if not self.metaRemain: #blank data case: meta is done too
				self.reset()

			return

		cAmt= min(self.dataRemain, len(_data)-self.dataPos )

		dataPosFrom= self.dataPos
		self.dataPos+= cAmt
		self.dataRemain-= cAmt

		self.dataCB and self.dataCB(_data[dataPosFrom:self.dataPos])
	
		if not self.dataRemain:
			logging.debug('Data finished')

			self.reset()



	def reset(self):
		self.meta= b''
		self.metaRemain= YiData.metaLength
		self.dataRemain= 0
