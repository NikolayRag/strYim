class KiLog():
	prefixOk= ''
	prefixErr= 'Error'

	logOk= True
	logErr= True
	def __init__(self, _pfxOk, _pfxErr):
		self.prefixOk= _pfxOk
		self.prefixErr= _pfxErr

	def ok(self, _msg):
		if not self.logOk:
			return
		print(self.prefixOk, _msg)

	def err(self, _msg):
		if not self.logErr:
			return
		print(self.prefixErr, _msg)

	def set(self, _ok=True, _err=True):
		self.logOk= _ok
		self.logErr= _err
