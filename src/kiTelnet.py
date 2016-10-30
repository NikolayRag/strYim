'''
Execute telnet command.



class KiTelnet(address, name, pass, cmd, callback, selfPort)
	Executes 'cmd' in specified telnet.
	To see result, use .result() or provide callback

	address
		Default ''
		Telnet address.

	user
		Defalt 'root'

	pass
		Default ''

	cmd
		Default ''
		Command to execute.

	callback(bytestring)
		Function to get partial console output as command is executing.
		if specified, command response is not returned by function itself.

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

	telnet= None
	telnetUser= ''
	telnetPass= ''

	selfAddr= ''



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




	def __init__(self
		, _telAddr
		, _telUser='root'
		, _telPass=''
		, _command=''
		, _cbRes=None
		, _selfPort=8088
		, _selfAddr=None
	):
#  todo 20 (telnet, log) +0: use log elseway

		self.blockedFlag= threading.Event()

		self.telnetUser= _telUser
		self.telnetPass= _telPass
		self.telnetAddr= _telAddr
		self.telnet= telnetlib.Telnet()


		if not _selfAddr:
			_selfAddr= self.localIp(_telAddr)
			
		if not _selfAddr:
			kiLog.err('No self IP')
			self.reset()
			return

		self.selfAddr= (_selfAddr, _selfPort)


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
			self.tcpSock.bind(self.selfAddr)
		except:
			kiLog.err('Cannot listen to %s' % str(self.selfAddr))
			self.reset()
			return

		self.tcpSock.listen(1)

		kiLog.ok('Tcp listening %s:%s...' % self.selfAddr)

		return True


	def tcpListen(self
		, _cbRes=None
		, _timeIn= 2	#not starting within
		, _timeOut= 5	#no output longer than
# =todo 8 (network) +0: check for timeout
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
			self.sendTelnet(self.telnetAddr, self.telnetUser, self.telnetPass, _command, self.selfAddr)
		except:
			if not self.blockedFlag.isSet():
				kiLog.err('Telnet error')
				self.reset()


	def sendTelnet(self
		, _addr
		, _log
		, _pass
		, _command
		, _addrOut
	):
		self.telnet.open(_addr)
		kiLog.ok("Telnet running:\n%s" % _command)

		self.telnet.read_until(self.telnetPromptLog)
		self.telnet.write( (_log +"\n").encode() )

		if _pass and _pass!='':
			self.telnet.read_until(self.telnetPromptPass)
			self.telnet.write( (_pass +"\n").encode() )

		self.telnet.read_until(self.telnetPrompt)
		req= {
			  'cmd':_command
			, 'ip':_addrOut[0]
			, 'port':_addrOut[1]
		}
		self.telnet.write( ("(%(cmd)s)| nc %(ip)s %(port)s >/dev/null\n" % req).encode() )
#  todo 19 (telnet) +0: get telnet finish elseway
		self.telnet.read_until(self.telnetPrompt) #wait for response
		self.telnet.close();




