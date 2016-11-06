import subprocess, threading, tempfile, os, re


class mp4RecoverExe():
	reAtom= re.compile('^\s*(?P<type>H264|AAC):\s+0x(?P<offset>[\dA-F]{8})\s+\[0x\s*(?P<len>[\dA-F]{1,8})\](\s+\{(?P<sign>([\dA-F]{2}\s*)+)\}\s+(?P<ftype>[A-Z]+)\s+frame)?$')
	cContext= None
	cFile= None

	cPos= 0
	foundAAC= []
	found264= []

	def __init__(self):
		self.foundAAC= []
		self.found264= []


	'''
	Provide raw mp4 data to parse.
	Return numer of bytes actually consumed.

		data
			byte string mp4 data

		context
			arbitrary identifier of supplied data

		final
			boolean, indicates no more data for this context will be sent (if consumed all).
	'''
	def parse(self, _data, _ctx, _final=False):
		if self.cContext!=_ctx:
			self.cContext= _ctx
			cFile= tempfile.NamedTemporaryFile(delete=False)
			self.cFile= cFile.name
			cFile.close()

			self.foundAAC= []
			self.found264= []
			self.cPos= 0


		kiLog.ok("%d MP4 %s data append to %s, final:%s" % (len(_data), self.cContext, self.cFile, _final))


		#store data
		cFile= open(self.cFile, 'ab')
		cFile.write(_data)
		cFile.close()

		#analyze data
		cwd= os.getcwd()
		os.chdir('D:/yi/restore/')
		recoverMeta= subprocess.check_output('recover_mp4_x64.exe "%s" --novideo --noaudio --ambarella --start %s' % (self.cFile, hex(self.cPos)), shell=True)
		recoverMetaA= recoverMeta.decode('ascii').split("\r\n")
		os.chdir(cwd)

		found264= []
		foundAAC= []


		cFile= open(self.cFile+'_.txt', 'a+')
		cFile.write(hex(self.cPos)+"\n")

		#deal with data
		#aac after last frame should be ignored untill it's not successful end of stream
		for cStr in recoverMetaA:
# =todo 44 (recover) +0: move start position as data recovered
			mp4Match= self.reAtom.match(cStr)
			if not mp4Match:
				continue

			cFile.write(cStr+"\n")

			atom= mp4Match.groupdict()
			atom= {'type':atom['type'], 'offset':int(atom['offset'],16), 'len':int(atom['len'],16), 'ftype':atom['ftype'], 'sign':bytes.fromhex(atom['sign'] or '')}
			if atom['type']=='H264':
				found264.append(atom)
				self.found264.append(atom)

			if atom['type']=='AAC':
				foundAAC.append(atom)
				self.foundAAC.append(atom)

			self.cPos= atom['offset']+ atom['len']

		cFile.close()

		kiLog.ok("%d frames in" % len(found264))




		if _final:
			kiLog.ok("%d h264, %d aac" % (len(self.found264), len(self.foundAAC)))

			if self.cFile:
				None
#				os.remove(self.cFile)

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
		kiLog.states(True, True, True, 'mp4RecoverExe')

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

