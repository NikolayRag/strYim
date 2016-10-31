'''
Execute telnet command.



class KiTelnet(address, name, pass, cmd, callback, selfPort)
	Executes 'cmd' in specified telnet.
	To see result, use .result() or provide callback

	cmd
		Default ''
		Command to execute.

	callback(bytestring)
		Function to get partial console output as command is executing.
		if specified, command response is not returned by function itself.

	address
		Default None
		Telnet address.

	user
		Defalt 'root'

	pass
		Default ''

	selfPort
		Default 8088
		Params for connecting to self from telnet.
		Should be firewall-enabled if telnet is remote.

	selfAddr
		Default None
		Local address for telnet to send results to.
		If not specified, will be tried to detected automatically
		 in same /24 net as specified telnet address.

result()
	Blocking.
	Return console output.
	If 'callback' was provided, empty string will return.
	Object is guaranteed stopped not after result()

	Return False on any error.
'''

import telnetlib, socket, threading

from .kiSupport import *
from .kiLog import *




class KiTelnet():
	kiLog.prefixes(
	      'KiTelnet log:'
	    , 'KiTelnet warning:'
	    , 'KiTelnet ERROR:'
	)



	tcpSock= None
	blockedFlag= None
	tcpResult= False


	telnetPromptLog= b'login: '
	telnetPromptPass= b'Password: '
	telnetPrompt= b' # '

	telnetAddr= None
	telnetUser= None
	telnetPass= None
	telnet= None

	selfAddr= None
	selfPort= None



	'''
	find local IP in in the same /24 network as given one
	'''
#  todo 6 (network, unsure) +0: think of telnet over route
	def localIp(self, _remoteIP):
		telIPA= str(_remoteIP).split('.')[0:3]

		for cIp in socket.gethostbyname_ex(socket.gethostname())[2]:
			if telIPA== str(cIp).split('.')[0:3]:
				return cIp

		return


	@staticmethod
	def defaults(
		  _telAddr=None
		, _telUser=None
		, _telPass=None
		, _selfPort=None
		, _selfAddr=None
	):
		if _selfAddr!=None:
			KiTelnet.selfAddr= _selfAddr
		if _selfPort!=None:
			KiTelnet.selfPort= _selfPort

		if _telAddr!=None:
			KiTelnet.telnetAddr= _telAddr
		if _telUser!=None:
			KiTelnet.telnetUser= _telUser
		if _telPass!=None:
			KiTelnet.telnetPass= _telPass



	def argsFill(self, _telAddr, _telUser, _telPass, _selfAddr, _selfPort):
		if _telAddr!=None:
			self.telnetAddr= _telAddr
		if self.telnetAddr==None:
			kiLog.err('missing telnet address')
			return

		if _telUser!=None:
			self.telnetUser= _telUser
		if self.telnetUser==None:
			kiLog.err('missing telnet user')
			return

		if _telPass!=None:
			self.telnetPass= _telPass
		if self.telnetPass==None:
			kiLog.err('missing telnet pass')
			return

		if not _selfAddr:
			_selfAddr= self.localIp(self.telnetAddr)

		if _selfAddr!=None:
			self.selfAddr= _selfAddr
		if self.selfAddr==None:
			kiLog.err('missing self address')
			return

		if _selfPort!=None:
			self.selfPort= _selfPort
		if self.selfPort==None:
			kiLog.err('missing self port')
			return

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
		, _cbRes=None
		, _telAddr=None
		, _telUser=None
		, _telPass=None
		, _selfPort=None
		, _selfAddr=None
	):
		self.telnet= telnetlib.Telnet()
		self.blockedFlag= threading.Event()


		if not self.argsFill(_telAddr, _telUser, _telPass, _selfAddr, _selfPort):
			self.reset()
			return


		if self.tcpPrepare():
			threading.Timer(0, lambda:self.tcpListen(_cbRes)).start()
			threading.Timer(0, lambda:self.tryTelnet(_command)).start()






	def result(self):
		self.blockedFlag.wait();

		if self.tcpResult==False:
			return False

		return self.tcpResult.decode('ascii')



	'''
	cancel everything and relax
	'''
	def reset(self, _soft=False):
		if self.tcpSock:
			self.tcpSock.close()
			self.tcpSock= None

		if not _soft:
			self.tcpResult= False

		self.blockedFlag.set()
		self.telnet.close()











	def tcpPrepare(self):
		self.tcpSock= socket.socket()

		try:
			self.tcpSock.bind((self.selfAddr,self.selfPort))
		except:
			kiLog.err('Cannot listen to port %s' % self.selfPort)
			self.reset()
			return

		self.tcpSock.listen(1)

		kiLog.ok('Tcp listening to port %s...' % self.selfPort)

		return True


	def tcpListen(self
		, _cbRes=None
		, _timeIn= 2	#not starting within
		, _timeOut= 5	#no output longer than
# -todo 8 (telnet) +0: check for timeout
	):

		tcpTimein= threading.Timer(_timeIn, self.tcpSock.close)
		tcpTimein.start()

		try:
			c, a= self.tcpSock.accept()
		except:
			kiLog.err('Tcp timeIn')
			self.reset()
			return

		tcpTimein.cancel()
		kiLog.ok('Tcp in from ' +a[0])


		self.tcpResult= b'';
		while 1:
			iIn= c.recv(1000000)
			if not iIn:
				break

			if not _cbRes:
				self.tcpResult+= iIn
			else:
				try:
					_cbRes(iIn)
				except:
					kiLog.err('Tcp callback exception')

		c.close()

		self.reset(True)



	def tryTelnet(self, _command):
		try:
			self.sendTelnet(_command)
		except:
			if not self.blockedFlag.isSet(): #not after end
				kiLog.err('Telnet error')
				self.reset()


	def sendTelnet(self, _command):
		self.telnet.open(self.telnetAddr)
		kiLog.ok("Telnet running:\n%s" % _command)

		self.telnet.read_until(self.telnetPromptLog)
		self.telnet.write( (self.telnetUser +"\n").encode() )

		if self.telnetPass:
			self.telnet.read_until(self.telnetPromptPass)
			self.telnet.write( (self.telnetPass +"\n").encode() )

		self.telnet.read_until(self.telnetPrompt)
		self.telnet.write( ("(%s)| nc %s %s >/dev/null\n" % (_command, self.selfAddr, self.selfPort)).encode() )
#  todo 19 (telnet) +0: get telnet finish elseway
		self.telnet.read_until(self.telnetPrompt) #wait for response
		self.telnet.close();




