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


	'''
	Run cleanup as function or as daemon.
	If daemon, fire and forget separate Python file. It should finish eventually.
	'''
	def fire(self, _daemon=False):
		if not _daemon:
			YiCleanup.cleanup(self.list)
			return


		with open(__file__+'.kill.py', 'w') as f:
			f.write('if True:\n') #fix indent
			f.write(''.join(inspect.getsourcelines(self.cleanup)[0][1:]))
			f.write('\ncleanup(["' +'","'.join(self.list) +'"])\n')

#		os.system('python '+__file__+'.kill.py')
		os.system('python '+__file__+'.kill.py &>/dev/null &')



### PRIVATE



	'''
	Delete files with several tries through YiAPI.
	'''
	@staticmethod
	def cleanup(filesA):
		import time, os, json, socket, re

		def delFile(f,yiSock, sessId, beat):
			yiSock.sendall( json.dumps({'msg_id':1281, 'token':sessId, "heartbeat":beat, "param":f}) )
			str= ''
			for n in range(5):
				str+= yiSock.recv(1024)
				for msgS in re.findall('(\{.*?\})', str):
					try:
						msg= json.loads(msgS)
						if ('msg_id' in msg) and msg['msg_id']==1281:
							return msg['rval']
					except:
						pass


		yiSock= socket.create_connection(('127.0.0.1',7878),1)
		yiSock.sendall( json.dumps({'msg_id':257}) )
		sessId= json.loads( yiSock.recv(1024).decode() )['param']
		beat= 0

		for f in filesA: #each file
			if os.path.isfile(f):
				for n in range(20): #tries
					beat+= 1
					if delFile(f, yiSock, sessId, beat)==0:
						break

					time.sleep(.5)

		beat+= 1
		yiSock.sendall( json.dumps({'msg_id':258, 'token':sessId, "heartbeat":beat}) )
		yiSock.close()



		os.remove(__file__) #kill self
