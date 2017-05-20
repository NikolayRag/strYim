import Yi4kAPI
import threading, re
import logging


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

	camMaskRe= re.compile('^.*(?P<dir>\d\d\d)MEDIA/L(?P<seq>\d\d\d)(?P<num>\d\d\d\d).MP4$')


	addr= None
	stopCB= None
	cleanFiles= True

	yi= None
	started= False
	settings= None



	def __init__(self, addr=None, _stopCB=None, _cleanFiles=True):
		self.addr= addr or self.addr

		self.stopCB= callable(_stopCB) and _stopCB

		self.cleanFiles= _cleanFiles
		


	'''
	_yiFormat is a (lines,fps)
	'''
	def start(self, _fps, _fmt):
		if self.started:
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
		self.started= True


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
			self.started= False

			return

		self.yi.setCB('video_record_complete', self.stopped)


		logging.info('Started %s' % set(yiFormat))
		return True



	def stop(self):
		if not self.started:
			logging.warning('Not started')
			return True #used also if externally stopped

		if not self.yi.sock:
			logging.error('Camera not found')
			return


		logging.info('Stopping')

		res= self.yi.cmd(Yi4kAPI.stopRecording)
#  todo 296 (Yi, fix) +0: camera stopped after stop sometimes
		if isinstance(res, int) and res<0:
			logging.warning('Stopping error: %s' % res)
			return

		return True




	'''
	Camera stopped
	'''
	def stopped(self, _res):
		logging.info('Stopped')
		self.started= False

		#delay closing YiAPI from YiAPI event
		threading.Timer(0, self.reset).start()

		self.stopCB and self.stopCB()




	'''
	Restore settings
	Delete remaining files and close YiAPI
	'''
	def reset(self):
		if self.settings:
			resA= [
				  self.yi.cmd(Yi4kAPI.setRecordMode, self.settings['rec_mode'])
				, self.yi.cmd(Yi4kAPI.setLoopDuration, self.settings['loop_rec_duration'])
				, self.yi.cmd(Yi4kAPI.setVideoQuality, self.settings['video_quality'])
				, self.yi.cmd(Yi4kAPI.setVideoStandard, self.settings['video_standard'])
				, self.yi.cmd(Yi4kAPI.setVideoResolution, self.settings['video_resolution'])
			]
			logging.info('Reset to: %s' % resA)


		self.yi.close()
