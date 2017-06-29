# -todo 306 (clean, YiAgent) +0: stop camera and restore settings in YiCleanup
'''
This module deletes video files by Yi API.
'''
class YiCleanup():
	import os, inspect
	global os, inspect

	limit= 5
	list= []



	def __init__(self, limit=5):
		self.limit= limit
		self.list= []



	'''
	Collect file names to be deleted later.
	'''
	def add(self, _file):
		if _file not in self.list:
			self.list= self.list[-self.limit+1:] +[_file]


	'''
	Run cleanup as function or as daemon.

	If daemon, orphan proccess is fired, allowing YiAgent to end up instantly.
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
	Delete video files.
	Try several times if files are locked.
 	
 	Files are deleted by lightweighted Yi API instead of direct deletion,
 	 because is deleted normally, they're are still being left in camera preview.
	'''
	@staticmethod
	def cleanup(filesA, _notDaemon=True):
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
		yiSock.settimeout(20)
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


#		if '_notDaemon' not in locals():
		os.remove(__file__) #kill self
