import subprocess, threading, tempfile, os


class mp4RecoverExe():
	cContext= None
	cFile= None
	cPos= 0

	def __init__(self):
		None


	'''
	Provide raw mp4 data to parse.
	Return numer of bytes actually consumed.

		data
			byte string mp4 data

		context
			arbitrary identifier of supplied data
	'''
	def parse(self, _data, _ctx):
		if not len(_data):
			if self.cFile:
				os.remove(self.cFile)
				return 0
			
		if self.cContext!=_ctx:
			self.cContext= _ctx
			cFile= tempfile.NamedTemporaryFile(delete=False)
			self.cFile= cFile.name
			cFile.close()


		kiLog.ok("%d MP4 data append to %s" % (len(_data), self.cFile))
		cFile= open(self.cFile, 'ab')
		cFile.write(_data)
		cFile.close()

		cwd= os.getcwd()
		os.chdir('D:/yi/restore/')
		recoverMeta= subprocess.check_output('recover_mp4_x64.exe "%s" --novideo --noaudio --ambarella --start %s' % (self.cFile, hex(self.cPos)), shell=True)
		os.chdir(cwd)
		cFile= open(self.cFile+'.txt', 'w')
		for cStr in recoverMeta.decode('ascii').split("\r\n")[0:]:
			cFile.write(cStr+"\n")
		cFile.close()
		
		return len(_data)








import sublime, sublime_plugin
from .byteTransit import *
from .kiYiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	def cbConn(self, _mode):
		kiLog.ok('Connected' if _mode else 'Disconnected')
	def cbLive(self, _mode):
		if _mode==1:
			kiLog.ok('Live')
		if _mode==-1:
			kiLog.ok('Dead')
	def cbAir(self, _mode):
		if _mode==1:
			kiLog.warn('Air On')
		if _mode==0:
			kiLog.warn('Air Off')
		if _mode==-1:
			kiLog.err('Air bad')

	def run(self, _edit):
		kiLog.states(True, True, True)

		if KiYi[0]:
			kiLog.warn('Already')
			return

		selfIP= KiTelnet.defaults('192.168.42.1', 'root', '', 8088)

		restoreO= mp4RecoverExe()
		buffer= byteTransit(restoreO.parse, 1000000)
		KiYi[0]= KiYiListener()
		KiYi[0].start(self.cbConn, self.cbLive)
		KiYi[0].live(buffer, self.cbAir)


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0].stop()
		KiYi[0]= None

