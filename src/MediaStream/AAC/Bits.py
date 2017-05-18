'''
Bits one-by-one streaming
'''
class Bits():
	gen= None

	left= 0
	got= 0


	'''
	Construct Int or Bytes from list of [(bits,value),..] pairs
	'''
	@staticmethod
	def bitsCollect(_bitPairs, _int=False):
		rlen= 0
		result= 0
		for cLen,cVal in _bitPairs:
			result= (result<<cLen) +cVal
			rlen+= cLen

		if _int:
			return result

		return result.to_bytes(int(rlen/8)+(rlen%8>0), 'big')



	def __init__ (self, _data=b''):
		self.left= len(_data) +1
		self.got= 0
		self.gen= self.bitGen(_data)


	def get (self, _num):
		out= 0

		for i in range(_num):
			out= out<<1
			if self.left:
				try:
					out+= next(self.gen)
				except:
					self.left= 0

		return out


	def bitGen (self, _bytes):
		for b in _bytes:
			self.left-= 1
			self.got+= 1
			for i in range(7,-1,-1):
				yield (b >> i) & 1

