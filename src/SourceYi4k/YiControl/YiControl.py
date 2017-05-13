import Yi4kAPI
import threading, re
import logging


# =todo 276 (Yi, fix) +0: update YiAPI and place it in YiControl
'''
Put camera in mode suitable for capturing stream.

Record is started with specified settings, which are restored
 after record is done.
'''
class YiControl():
	presets= {
		  (1440, 60):"1920x1440 60P 4:3"
		, (1440, 30):"1920x1440 30P 4:3"
		, (1080, 60):"1920x1080 60P 16:9"
		, (1080, 30):"1920x1080 30P 16:9"
	}
	deleteCMD= Yi4kAPI.YiAPICommandGen(1281, 'deleteFile', 	variable= 'param')
	camMaskRe= re.compile('^.*(?P<dir>\d\d\d)MEDIA/L(?P<seq>\d\d\d)(?P<num>\d\d\d\d).MP4$')


	addr= None
	stopCB= None
	cleanFiles= True

	yi= None
	settings= None



	def __init__(self, addr=None, _stopCB=None, _cleanFiles=True):
		self.addr= addr or self.addr

		self.stopCB= callable(_stopCB) and _stopCB

		self.cleanFiles= _cleanFiles
		


	'''
	_yiFormat is a (lines,fps)
	'''
	def start(self, _fps, _fmt):
		if self.yi:
			logging.error('Already started')
			return

		yiFormat= (_fmt, _fps)
		if yiFormat not in self.presets:
			logging.error('Unknown mode')
			return 


		self.yi= Yi4kAPI.YiAPI(self.addr)
		if not self.yi.sock:
			logging.error('Camera not found')
			return


		self.settings= self.yi.cmd(Yi4kAPI.getSettings)

		resA= [
			  self.yi.cmd(Yi4kAPI.setRecordMode, 'record_loop')
			, self.yi.cmd(Yi4kAPI.setLoopDuration, '5 minutes')
			, self.yi.cmd(Yi4kAPI.setVideoQuality, 'normal')
			, self.yi.cmd(Yi4kAPI.setVideoStandard, 'NTSC')
			, self.yi.cmd(Yi4kAPI.setVideoResolution, self.presets[yiFormat])
		]
		logging.info('Set to: %s' % resA)

		res= self.yi.cmd(Yi4kAPI.startRecording)
		if res:
			logging.error('Starting error: %s' % res)
			self.yi.close()

			return

		self.yi.setCB('video_record_complete', self.stopped)


		logging.info('Started %s' % set(yiFormat))
		return True



	def stop(self):
		if not self.yi:
			logging.warning('Not started')
			return True #used also if externally stopped

		if not self.yi.sock:
			logging.error('Camera not found')
			return


		logging.info('Stopping')

		res= self.yi.cmd(Yi4kAPI.stopRecording)
		if isinstance(res, int) and res<0:
			logging.error('Stopping error: %s' % res)
			return

		return True




	'''
	Camera stopped
	'''
	def stopped(self, _res):
		logging.info('Stopped')

		cYi= self.yi
		self.yi= None

		threading.Timer(0, lambda:self.reset(cYi)).start()


		fNameMatch= self.camMaskRe.match(_res['param'])
		lastDir= int(fNameMatch.group('dir'))
		lastLoop= int(fNameMatch.group('seq'))
		lastFile= int(fNameMatch.group('num'))

		#delay closing YiAPI from YiAPI event
# -todo 281 (YiAgent, clean) +0: cleanup releasing last file for deletion
		threading.Timer(5, lambda: self.cleanup(cYi, lastDir, lastLoop, lastFile)).start()


		self.stopCB and self.stopCB()




	'''
	Restore settings
	'''
	def reset(self, _cYi):
		if not self.settings:
			return

		resA= [
			  _cYi.cmd(Yi4kAPI.setRecordMode, self.settings['rec_mode'])
			, _cYi.cmd(Yi4kAPI.setLoopDuration, self.settings['loop_rec_duration'])
			, _cYi.cmd(Yi4kAPI.setVideoQuality, self.settings['video_quality'])
			, _cYi.cmd(Yi4kAPI.setVideoStandard, self.settings['video_standard'])
			, _cYi.cmd(Yi4kAPI.setVideoResolution, self.settings['video_resolution'])
		]
		logging.info('Reset to: %s' % resA)


	'''
	Delete remaining files and close YiAPI
	'''
	def cleanup(self, _cYi, _lastDir, _lastLoop, _lastFile):
		if self.cleanFiles:
			filesDeleted= 0
			for n in range(5):
				if _cYi.cmd(self.deleteCMD, '/tmp/fuse_d/DCIM/%03dMEDIA/L%03d%04d.MP4' % (_lastDir, _lastLoop, _lastFile))==None:
					filesDeleted+=1

				_lastFile-= 1
				if _lastFile==0:
					_lastFile= 999
					_lastDir-= 1

			logging.info('Deleted %d files' % filesDeleted)


		_cYi.close()
