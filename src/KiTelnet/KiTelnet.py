'''
Execute telnet command in background.
Returns result at demand or using callback.


class KiTelnet(cmd, [address], [user], [pass])
	Executes 'cmd' in specified telnet.
	To see result, use .result([callback])

	cmd
		Default ''
		Command to execute.

	address
		Default None
		Telnet address.

	user
		Defalt 'root'

	pass
		Default ''

	callback(bytestring)
		Function to get partial console output as command is executing.
		if specified, result() will return blank string.


result()
	Blocking.
	Return telnet output,
	 or False on any error.
'''

import telnetlib, socket, threading

import logging



class KiTelnet():
	blockedFlag= None
	telnetResult= False
	telnetCB= None

	telnetPromptLog= b'login: '
	telnetPromptPass= b'Password: '
	telnetPrompt= b' # '

	telnetAddr= None
	telnetUser= 'root'
	telnetPass= ''

	telnet= None




	@staticmethod
	def defaults(
		  address=None
		, user=None
		, password=None
	):
		if address!=None:
			KiTelnet.telnetAddr= address
		if user!=None:
			KiTelnet.telnetUser= user
		if password!=None:
			KiTelnet.telnetPass= password



	def argsFill(self, _telAddr, _telUser, _telPass):
		if _telAddr!=None:
			self.telnetAddr= _telAddr
		if self.telnetAddr==None:
			logging.error('missing telnet address')
			return

		if _telUser!=None:
			self.telnetUser= _telUser
		if self.telnetUser==None:
			logging.error('missing telnet user')
			return

		if _telPass!=None:
			self.telnetPass= _telPass

		return True




	'''
	Constructor.
	Provided command is started to execute without delay.
	Result is fetched with .result(), blocking until command is finished.

	If not provided, telnet and network parameters are taken from defaults,
	 which are set by defaults() static method.
	'''
	def __init__(self
		, _command=''
		, address=None
		, user=None
		, password=None
		, callback=None
	):
		self.blockedFlag= threading.Event()


		if not self.argsFill(address, user, password):
			self.finish(False)
			return


		threading.Timer(0, lambda:self.tryTelnet(_command)).start()





	def result(self, _cb=None):
		if callable(_cb):
			self.telnetCB= _cb
			return True


		self.blockedFlag.wait();

		return self.telnetResult








	'''
	Finish everything and relax
	'''
	def finish(self, _result):
		if self.telnet:
			self.telnet.close()


		self.telnetResult= _result

		#callback hook
		if self.telnetCB:
			self.telnetCB(_result)
			self.telnetResult= True


		self.blockedFlag.set()



	'''
	Telnet fallback wrapper
	'''
	def tryTelnet(self, _command):
		result= False
		try:
			result= self.runTelnet(_command)
		except:
			logging.error('Telnet error')

		self.finish(result)



	def runTelnet(self, _command):
		self.telnet= telnetlib.Telnet()

		self.telnet.open(self.telnetAddr, 23, 7)
		logging.info("Telnet running: %s" % _command)
		self.telnet.get_socket().settimeout(None)

		self.telnet.read_until(self.telnetPromptLog)
		self.telnet.write( (self.telnetUser +"\n").encode() )

		if self.telnetPass:
			self.telnet.read_until(self.telnetPromptPass)
			self.telnet.write( (self.telnetPass +"\n").encode() )

		self.telnet.read_until(self.telnetPrompt)

		cCmd= (_command +";exit\r\n").encode()
		self.telnet.write(cCmd)
		self.telnet.read_until(b';exit\r\n') #skip command echo

		return self.telnet.read_all()
