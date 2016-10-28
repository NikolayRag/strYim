class KiLog():
	prefixOk= ''
	prefixErr= 'Error'

	def __init__(self, _pfxOk, _pfxErr):
		self.prefixOk= _pfxOk
		self.prefixErr= _pfxErr

	def ok(self, _msg):
		print(self.prefixOk, _msg)

	def err(self, _msg):
		print(self.prefixErr, _msg)

