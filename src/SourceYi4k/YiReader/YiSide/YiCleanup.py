'''
This module deletes video files in very background, allowing application
 to end and camera connection to stop without waiting for locked files.

First filenames to be deleted are collected.
Then, at the end of recording, orphan daemon proccess is fired,
 allowing YiAgent to end up instantly.
Daemon is waiting for a while, trying to delete recorded files
 by lightweighted YiAPI, because files deleted normally are still
 being left in camera preview till restart.
'''
class YiCleanup():
	import os, inspect
	global os, inspect

	limit= 5
	list= []



	def __init__(self, limit=5):
		self.limit= limit
		self.list= []



	def add(self, _file):
		if _file not in self.list:
			self.list= self.list[-self.limit+1:] +[_file]



	def fire(self):
		with open(__file__+'.kill.py', 'w') as f:
			f.write('def start():\n')
			f.write(''.join(inspect.getsourcelines(self.__cleanupDaemon)[0][1:]))
			f.write('\nstart()')

#		os.system('python '+__file__+'.kill.py ' +' '.join(self.list))
		os.system('python '+__file__+'.kill.py ' +' '.join(self.list)+ ' &>/dev/null &')



	'''
	Contents are executed in separate background Python on camera side.
	Treat this code as plain.
	'''
	def __cleanupDaemon():
		import time, os, sys, json, socket


		def killWithApi(_file):
			yiSock= socket.create_connection(('127.0.0.1',7878),1)
			yiSock.sendall( json.dumps({'msg_id':257}) )
			sessId= json.loads( yiSock.recv(1024).decode() )['param']

			yiSock.sendall( json.dumps({'msg_id':1281, 'token':sessId, "heartbeat":1, "param":_file}) )
			res= json.loads( yiSock.recv(1024).decode() )['rval']

			yiSock.sendall( json.dumps({'msg_id':258, 'token':sessId, "heartbeat":2}) )
			yiSock.recv(1024)
			yiSock.close


			return res==0



		countDel= 0
		for f in sys.argv[1:]:
			if os.path.isfile(f):
				for n in range(10):
					if killWithApi(f):
						countDel+= 1
						break

					time.sleep(1)


		print(countDel)

		os.remove(__file__) #kill self
