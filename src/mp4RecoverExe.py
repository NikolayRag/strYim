import subprocess, tempfile, os, re

from .byteTransit import *
from .kiLog import *


class Atom():
	type= None
	data= None

	def __init__(self, _type=None, _data=b''):
		self.type= _type
		self.data= _data



# =todo 101 (recover) +2: use native atoms searching: [h264, aac, ...]
class Mp4Recover():
	h264Presets= {
		  (1080,30,0): b'\'M@3\x9ad\x03\xc0\x11?,\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea`\xe8`\x00\xb7\x18\x00\x02\xdcl\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00[\x8d\x97ypxD"R\xc0'
		, -1: b'\x28\xee\x38\x80'
	}


	reAtom= re.compile('^\s*(?P<atype>H264|AAC):\s+0x(?P<offset>[\dA-F]{8})\s+\[0x\s*(?P<len>[\dA-F]{1,8})\](\s+\{(?P<sign>([\dA-F]{2}\s*)+)\}\s+(?P<type>[A-Z]+)\s+frame)?$')
	cContext= None
	cFile= None
	safePos= 0

	transit= None

	atomCB=None


	def __init__(self, _atomCB):
		self.transit= byteTransit(self.parse, 1000000)


		self.atomCB= _atomCB

		if callable(self.atomCB):
			self.atomCB( Atom('IDR',self.h264Presets[(1080,30,0)]) )
			self.atomCB( Atom('IDR',self.h264Presets[-1]) )
		

	def add(self, _data, _ctx=None):
		self.transit.add()



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
	def parse(self, _data, _ctx, _finalize=False):
		self.checkContext(_ctx)
		self.holdData(_data)
		recoverAtoms= self.analyze(_finalize)

		firstIDR= 0
		for atom in recoverAtoms:
			if atom['type']=='IDR':
				break

			firstIDR+= 1

		kiLog.ok("%d atoms, %d skipped%s" % (len(recoverAtoms)-firstIDR, firstIDR, ', finaly' if _finalize else '') )


		if callable(self.atomCB):
			cFile= open(self.cFile, 'rb')

			for atom in recoverAtoms[firstIDR:]:
				preSize= 4 if atom['type'] else 0 #skip ui32 size for 264 atoms

				cFile.seek( int(atom['offset'],16)+preSize )
				restoredData= cFile.read( int(atom['len'],16)-preSize )

				self.atomCB( Atom(atom['type'],restoredData) )

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

			self.safePos= '0'


	def holdData(self, _data):
		cFile= open(self.cFile, 'ab')
		cFile.write(_data)
		cFile.close()


	def analyze(self, _finalize):
		try:
			os.chdir('D:/yi/restore/')
			recoverMeta= subprocess.check_output('recover_mp4_x64.exe "%s" --novideo --noaudio --ambarella --start %s' % (self.cFile, self.safePos), shell=True)
		except:
			recoverMeta= b''


		atomsA= []
		lastFrameI= None
		for cStr in recoverMeta.decode('ascii').split("\r\n"):
			mp4Match= self.reAtom.match(cStr)
			if mp4Match:
				mp4Match= mp4Match.groupdict()

				#last frame and remaining should be left to next run untill it's not final
				if not _finalize and mp4Match['type']=='IDR':
					self.safePos= mp4Match['offset']
					lastFrameI= len(atomsA)

				atomsA.append(mp4Match)


		return atomsA[:lastFrameI]



