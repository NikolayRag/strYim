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

	silent
		Default False
		Dont collect command response. Use when expecting a lot to return, use callback instead.
'''

import telnetlib, socket, threading

from .kilog import *


class KiTelnet():
	tcpThread= None
	tcpSock= None
	tcpEvt= None
	tcpResult= b''


	telnetUser= ''
	telnetPass= ''
	telnetAddr= ''

	selfAddr= ''


	log= KiLog('KiTelnet log:', 'KiTelnet ERROR:')


	def __init__(self, _telAddr, _telUser='root', _telPass='', _selfPort=8088):
		self.tcpEvt= threading.Event()

		self.telnetUser= _telUser
		self.telnetPass= _telPass
		self.telnetAddr= _telAddr

		selfIP= self.detectIp(_telAddr)
		if selfIP:
			self.log.ok('Self IP used: %s' % selfIP)

		self.selfAddr= (selfIP, _selfPort)



	'''
	find local IP in in the same /24 network as given one
	'''
	def detectIp(self, _telIP):
		telIPA= str(_telIP).split('.')[0:3]

		for cIp in socket.gethostbyname_ex(socket.gethostname())[2]:
			if telIPA== str(cIp).split('.')[0:3]:
				return cIp

		return




	def command(self
		, _command
		, _cbTCP=None
		, _noreturn=False
	):
		if not self.selfAddr[0]:
			self.log.err('Network configuration')
			return

		if self.tcpThread:
			return

		self.tcpEvt.clear();

		self.tcpThread= threading.Timer(0, lambda:self.tcpListen(_cbTCP, _noreturn))
		self.tcpThread.start()
		try:
			self.sendTelnet(self.telnetAddr, self.telnetUser, self.telnetPass, _command, self.selfAddr)
		except:
			self.log.err('Telnet error')
			self.tcpEvt.set();


		self.tcpEvt.wait();

		self.tcpThread= None #reset

		if self.tcpResult==False:
			self.log.err('Execution')
			return False


		self.log.ok('Executed with %d bytes' % len(self.tcpResult))

		return self.tcpResult.decode('ascii')



	def tcpListen(self
		, _cbTCP=None
		, _noreturn=False
		, _timeoutIn= 5		#not starting within
		, _timeoutOut= 60	#transfer longer than
	):
		self.tcpSock= socket.socket()
		try:
			self.tcpSock.bind(self.selfAddr)
		except:
			self.log.err('No camera')
			self.tcpSock.close()
			self.tcpEvt.set();

			self.tcpResult= False
			return

		self.tcpSock.listen(1)

		tcpTimeinSteady= threading.Timer(_timeoutIn, self.tcpSock.close)
		tcpTimeinSteady.start()

		self.log.ok('Tcp listening %s:%s...' % self.selfAddr)
		try:
			c, a= self.tcpSock.accept()
		except:
			self.log.err('Tcp timeIn')

			self.tcpThread.cancel()
			self.tcpEvt.set();

			self.tcpResult= False
			return

		self.log.ok('Tcp in from ' +a[0])
		tcpTimeinSteady.cancel()

		self.tcpResult= b'';
		while 1:
			iIn= c.recv(1000000)
			if not iIn:
				break

			if not _noreturn:
				self.tcpResult+= iIn

			if _cbTCP:
				try:
					_cbTCP(iIn)
				except:
					self.log.err('Tcp callback exception')

		c.close()
		self.tcpSock.close()
		self.tcpEvt.set();



	def sendTelnet(self
		, _addr
		, _log
		, _pass
		, _command
		, _addrOut
	):
		self.log.ok("Telnet running:\n%s" % _command)

		req= {'ip':_addrOut[0], 'port':_addrOut[1]}

		t= telnetlib.Telnet(_addr)
		t.read_until(b'a9s login: ')
		t.write( (_log +"\n").encode() )

		if _pass and _pass!='':
			t.read_until(b'Password: ')
			t.write( (_pass +"\n").encode() )

		t.read_until(b' # ')
		t.write( (_command +"| nc %(ip)s %(port)s >/dev/null\n" % req).encode() )
		t.read_until(b' # ') #wait for response
		t.close();

		self.log.ok("Telnet ok")
