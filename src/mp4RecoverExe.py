import subprocess, tempfile, os, re

from .byteTransit import *
from .mp4Atom import *
from .kiLog import *




class Mp4RecoverExe():
	h264Presets= {
		  (1080,30,0): b'\'M@3\x9ad\x03\xc0\x11?,\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea`\xe8`\x00\xb7\x18\x00\x02\xdcl\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00[\x8d\x97ypxD"R\xc0'
		, -1: b'\x28\xee\x38\x80'
	}


	reMp4Match= re.compile('^\s*(?P<atype>H264|AAC):\s+0x(?P<offset>[\dA-F]{8})\s+\[0x\s*(?P<len>[\dA-F]{1,8})\](\s+\{(?P<sign>([\dA-F]{2}\s*)+)\}\s+(?P<type>[A-Z]+)\s+frame)?$')
	cFile= None
	safePos= 0

	transit= None

	atomCB=None


	def __init__(self, _atomCB):
		self.setContext()
		self.transit= byteTransit(self.parse, 1000000)


		self.atomCB= _atomCB

		if callable(self.atomCB):
			self.atomCB( Atom(data=self.h264Presets[(1080,30,0)]).setAVC(True,False) )
			self.atomCB( Atom(data=self.h264Presets[-1]).setAVC(True,False) )
		

	def add(self, _data, _ctx=None):
		self.transit.add(_data, _ctx)



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
	def parse(self, _data, _finalize=False):
		self.holdData(_data)
		recoverMatchesA= self.analyze(_finalize, self.cFile, self.safePos)

		firstIDR= 0
		for match in recoverMatchesA:
			if match['type']=='IDR':
				break

			firstIDR+= 1

		kiLog.ok("%d matches, %d skipped%s" % (len(recoverMatchesA)-firstIDR, firstIDR, ', finaly' if _finalize else '') )


		if callable(self.atomCB):
			cFile= open(self.cFile, 'rb')

			for match in recoverMatchesA[firstIDR:]:
				preSize= 4 if match['type'] else 0 #skip ui32 size for 264 atoms

				cFile.seek( int(match['offset'],16)+preSize )
				restoredData= cFile.read( int(match['len'],16)-preSize )

				atomOut= Atom(data=restoredData).setAVC(True)
				if match['type']:
					atomOut.setAVC(match['type']=='IDR')
				else:
					atomOut.setAAC()

				self.atomCB( atomOut )

			cFile.close()



		#clean
		if _finalize and self.cFile:
			self.setContext()


		return len(_data) #all been consumed to file




	def setContext(self):
		if self.cFile:
			os.remove(self.cFile)

		cFile= tempfile.NamedTemporaryFile(delete=False)
		self.cFile= cFile.name
		cFile.close()

		self.safePos= '0'


	def holdData(self, _data):
		cFile= open(self.cFile, 'ab')
		cFile.write(_data)
		cFile.close()


	def analyze(self, _finalize, _file, _start):
		try:
			os.chdir('D:/yi/restore/')
			recoverMeta= subprocess.check_output('recover_mp4_x64.exe "%s" --novideo --noaudio --ambarella --aacmin 0x100 --start %s' % (_file, _start), shell=True)
		except:
			recoverMeta= b''


		matchesA= []
		lastFrameI= None	#Last IDR frame to cut out if not finalize
		aacFrame= None		#interframe aac to collect
		for cStr in recoverMeta.decode('ascii').split("\r\n"):
			mp4Match= self.reMp4Match.match(cStr)
			if mp4Match:
				mp4Match= mp4Match.groupdict()

				#last frame and remaining should be left to next run untill it's not final
				if not _finalize and mp4Match['type']=='IDR':
					self.safePos= mp4Match['offset']
					lastFrameI= len(matchesA)

				matchesA.append(mp4Match)



		return matchesA[:lastFrameI]



