import subprocess, tempfile, os, re

from .kiLog import *


class mp4RecoverExe():
	reAtom= re.compile('^\s*(?P<type>H264|AAC):\s+0x(?P<offset>[\dA-F]{8})\s+\[0x\s*(?P<len>[\dA-F]{1,8})\](\s+\{(?P<sign>([\dA-F]{2}\s*)+)\}\s+(?P<ftype>[A-Z]+)\s+frame)?$')
	cContext= None
	cFile= None
	cPos= 0

	atomCB=None

	def __init__(self, _atomCB):
		self.atomCB= _atomCB


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
#  todo 64 (mp4) +0: allow start only from 264 frame
	def parse(self, _data, _ctx, _finalize=False):
		self.checkContext(_ctx)
		self.holdData(_data)
		recoverAtoms= self.analyze(_finalize)

		kiLog.ok("%d atoms%s" % (len(recoverAtoms), ', finaly' if _finalize else '') )

		if callable(self.atomCB):
			cFile= open(self.cFile, 'rb')

			for atom in recoverAtoms:
				cFile.seek(atom['offset'])
				b264= cFile.read(atom['len'])

				self.atomCB(atom, b264)

			cFile.close()



		#clean
		if _finalize and self.cFile:
			os.remove(self.cFile)


		return len(_data) #all been consumed




	def checkContext(self, _ctx):
		if self.cContext!=_ctx:
			self.cContext= _ctx
			cFile= tempfile.NamedTemporaryFile(delete=False)
			self.cFile= cFile.name
			cFile.close()

			self.cPos= 0


	def holdData(self, _data):
		cFile= open(self.cFile, 'ab')
		cFile.write(_data)
		cFile.close()


	def analyze(self, _finalize):
		try:
			os.chdir('D:/yi/restore/')
			recoverMeta= subprocess.check_output('recover_mp4_x64.exe "%s" --novideo --noaudio --ambarella --start %s' % (self.cFile, hex(self.cPos)), shell=True)
		except:
			recoverMeta= b''


		atomsA= []
		lastFrameI= None
		for cStr in recoverMeta.decode('ascii').split("\r\n"):
			mp4Match= self.reAtom.match(cStr)
			if mp4Match:
				atom= {'type':mp4Match.group('type'), 'offset':int(mp4Match.group('offset'),16), 'len':int(mp4Match.group('len'),16), 'ftype':mp4Match.group('ftype'), 'sign':bytes.fromhex(mp4Match.group('sign') or '')}

				#last frame and remaining should be left to next run untill it's not final
				if not _finalize and atom['type']=='H264':
					self.cPos= atom['offset']
					lastFrameI= len(atomsA)

				atomsA.append(atom)


		return atomsA[:lastFrameI]



