import socket, json, time

from .kiLog import *



'''
Limited version of Yi4k API.
Supports only settings and states.

'''


class YiAPICommand():
	id= None
	cb= None

	def __init__(self, _id, _cb=None):
		self.id= int(_id)
		self.cb= _cb



class YiAPI():
	def StartSessionCommandCB(_ctx):
		_ctx.sessionId= _ctx.res['param']
	StartSessionCommand= YiAPICommand(257, StartSessionCommandCB)

	StopSessionCommand= YiAPICommand(258)

	GetSettingsCommand= YiAPICommand(3)


	sock= None
	tick= 0
	sessionId= 0




	def __init__(self):
		self.sock= socket.create_connection(('192.168.42.1',7878))

		self.cmd(YiAPI.StartSessionCommand)

	#shoud be called at very end to tell camera it's released
	def stop(self):
		self.cmd(YiAPI.StopSessionCommand)

		self.sock= None



	def cmd(self, _command):
		if not self.sock:
			kiLog.err('Camera disconnected')
			return -1


		self.sock.sendall(self.cmdString(_command.id))

		self.sock.settimeout(1)	#wait for a while for camera to execute command
		resBytes= b''
		while True:
			try:
				recv= self.sock.recv(8192)
				resBytes+= recv

				self.sock.settimeout(.1) #wait a little for detect end-of-data
			except:
				break


		kiLog.verb("Recieved from Yi: %d %s" % (len(resBytes), resBytes))
		try:
			self.res= json.loads(resBytes.decode())
		except:
			return -2

		if not self.res['rval']:
			if callable(_command.cb):
				_command.cb(self)

		return self.res['rval']




	def cmdString(self, _id):
		out= {'msg_id':_id, 'token':self.sessionId}
		if self.tick:
			out['heartbeat']= self.tick
		self.tick+= 1

		kiLog.verb("Send to Yi: %s" % out)
		
		return bytes(json.dumps(out),'ascii')



