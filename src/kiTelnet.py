'''
execute command in Yi 4k telnet environment


class KiTelnet(name, pass, address)
		Only prepares parameters for connection.

	address
		Default ''

	user
		Defalt 'root'

	pass
		Default ''

	selfPort
		Default: 8088

		Params for connecting to telnet.

command(cmd, callback, silent)
	Executes CMD and return its console output.

	cmd
		Default ''
		Command to execute.

	callback(bytestring)
		Function to get partial console output as command is executing.
		if specified, command response is not returned by function itself.
'''

import telnetlib, socket, threading

from .kilog import *


class KiTelnet():
	tcpSock= None
	blockedFlag= None
	tcpResult= False


	telnet= None
	telnetUser= ''
	telnetPass= ''
	telnetAddr= ''

	selfAddr= ''


	log= KiLog('KiTelnet log:', 'KiTelnet ERROR:')


	def __init__(self, _telAddr, _telUser='root', _telPass='', _selfPort=8088):
		self.blockedFlag= threading.Event()
		self.blockedFlag.set();

		self.telnetUser= _telUser
		self.telnetPass= _telPass
		self.telnetAddr= _telAddr

		selfIP= self.detectIp(_telAddr)
		if selfIP:
			self.log.ok('Self IP used: %s' % selfIP)

		self.selfAddr= (selfIP, _selfPort)



	'''
	switch logging
	'''
	def logMode(self, _ok=True, _err=True):
		self.log.set(_ok, _err)



	'''
	find local IP in in the same /24 network as given one
	'''
#  todo 6 (network, unsure) +0: think of telnet over route
	def detectIp(self, _telIP):
		telIPA= str(_telIP).split('.')[0:3]

		for cIp in socket.gethostbyname_ex(socket.gethostname())[2]:
			if telIPA== str(cIp).split('.')[0:3]:
				return cIp

		return




	def command(self
		, _command
		, _cbTCP=None
	):
		if not self.selfAddr[0]:
			self.log.err('Network configuration')
			return

		if not self.blockedFlag.isSet():
			return

		self.blockedFlag.clear();

		self.tcpPrepare()

		threading.Timer(0, lambda:self.tcpListen(_cbTCP)).start()

#  todo 11 (code) +0: call telnet unblocking
#		threading.Timer(0, lambda:self.tryTelnet(_command)).start()
		self.tryTelnet(_command)

		self.blockedFlag.wait();


		if self.tcpResult==False:
			self.log.err('')
			return False

		self.log.ok('Executed with %d bytes' % len(self.tcpResult))

		return self.tcpResult.decode('ascii')



	'''
	cancel everything and relax
	'''
	def reset(self, _soft=False):
		if self.tcpSock:
			self.tcpSock.close()
			self.tcpSock= None

#		if self.telnet:
#			self.telnet.close()

		if not _soft:
			self.tcpResult= False

		self.blockedFlag.set()




	def tcpPrepare(self):
		self.tcpSock= socket.socket()

		try:
			self.tcpSock.bind(self.selfAddr)
		except:
			self.log.err('No camera')
			self.reset()
			return

		self.tcpSock.listen(1)

		self.log.ok('Tcp listening %s:%s...' % self.selfAddr)



	def tcpListen(self
		, _cbTCP=None
		, _timeoutIn= 5		#not starting within
#		, _timeoutOut= 60	#transfer longer than
#  todo 8 (network) +0: check for timeout
	):

		tcpTimeinSteady= threading.Timer(_timeoutIn, self.tcpSock.close)
		tcpTimeinSteady.start()

		try:
			c, a= self.tcpSock.accept()
		except:
			self.log.err('Tcp timeIn')
			self.reset()
			return

		tcpTimeinSteady.cancel()
		self.log.ok('Tcp in from ' +a[0])

		self.tcpResult= b'';
		while 1:
			iIn= c.recv(1000000)
			if not iIn:
				break

			if not _cbTCP:
				self.tcpResult+= iIn
			else:
				try:
					_cbTCP(iIn)
				except:
					self.log.err('Tcp callback exception')

		c.close()

		self.reset(True)



	def tryTelnet(self, _command):
		try:
			self.sendTelnet(self.telnetAddr, self.telnetUser, self.telnetPass, _command, self.selfAddr)
		except:
			if not self.blockedFlag.isSet():
				self.log.err('Telnet error')
				self.reset()


	def sendTelnet(self
		, _addr
		, _log
		, _pass
		, _command
		, _addrOut
	):
		self.log.ok("Telnet running:\n%s" % _command)

		self.telnet= telnetlib.Telnet(_addr)
		self.telnet.read_until(b'a9s login: ')
		self.telnet.write( (_log +"\n").encode() )

		if _pass and _pass!='':
			self.telnet.read_until(b'Password: ')
			self.telnet.write( (_pass +"\n").encode() )

		self.telnet.read_until(b' # ')
		req= {
			  'cmd':_command
			, 'ip':_addrOut[0]
			, 'port':_addrOut[1]
		}
		self.telnet.write( ("(%(cmd)s)| nc %(ip)s %(port)s >/dev/null\n" % req).encode() )
		self.telnet.read_until(b' # ') #wait for response
		self.telnet.close();

		self.log.ok("Telnet ok")
