'''
Storage class used to pass AVC/ACC data from Mp4Recover to muxers
'''
class Atom():
	typeMoov= False
	typeAVC= False
	typeAAC= False

	AVCKey= None
	AVCVisible= None

	AACSamples= None

	inPos= None
	outPos= None

	data= None


	def __init__(self, _in=None, _out=None, data=None):
		self.inPos= _in
		self.outPos= _out
		if data:
			self.data= data[_in:_out]


	def setMOOV(self):
		self.typeMoov= True
		self.typeAVC= False
		self.typeAAC= False

		return self


	def setAVC(self, _key=False, _visible=True):
		self.typeMoov= False
		self.typeAVC= True
		self.typeAAC= False
		self.AVCKey= _key
		self.AVCVisible= _visible

		return self


	def setAAC(self):
		self.typeMoov= False
		self.typeAVC= False
		self.typeAAC= True

# -todo 117 (mux, flv, bytes, aac) +2: reveal actual AAC frame length
		self.AACSamples= 1024

		return self


# -todo 128 (bytes) +0: use memoryview as binded data
	def bindData(self, _data):
		self.data= _data[self.inPos:self.outPos]

		return self

