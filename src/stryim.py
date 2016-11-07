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


		#store data
		cFile= open(self.cFile, 'ab')
		cFile.write(_data)
		cFile.close()

		#analyze data
		cwd= os.getcwd()
		os.chdir('D:/yi/restore/')
		recoverMeta= subprocess.check_output('recover_mp4_x64.exe "%s" --novideo --noaudio --ambarella --start %s' % (self.cFile, hex(self.cPos)), shell=True)
		os.chdir(cwd)


		recoverAtoms= []
		recoverLastFrame= None
		for cStr in recoverMeta.decode('ascii').split("\r\n"):
			mp4Match= self.reAtom.match(cStr)
			if mp4Match:
				atom= {'type':mp4Match.group('type'), 'offset':int(mp4Match.group('offset'),16), 'len':int(mp4Match.group('len'),16), 'ftype':mp4Match.group('ftype'), 'sign':bytes.fromhex(mp4Match.group('sign') or '')}
				recoverAtoms.append(atom)

				#atoms after last frame should be ignored untill it's not successful end of stream
				if not _final and atom['type']=='H264':
					recoverLastFrame= len(recoverAtoms)

		found264= []
		foundAAC= []


		cFile= open(self.cFile+'_.txt', 'a+')
		cFile.write(hex(self.cPos)+"\n")

		#deal with data
		for atom in recoverAtoms[:recoverLastFrame]:
			cFile.write(str(atom)+"\n")

			if atom['type']=='H264':
				found264.append(atom)
				self.found264.append(atom)

			if atom['type']=='AAC':
				foundAAC.append(atom)
				self.foundAAC.append(atom)

			self.cPos= atom['offset']+ atom['len']

		cFile.close()

		kiLog.ok("%d frames in%s" % (len(found264), ', finaly' if _final else '') )




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

