import Yi4kAPI
import threading
import logging


# =todo 276 (Yi, fix) +0: update YiAPI and place it in YiControl
class YiControl():
	presets= {
		  (1440, 60):"1920x1440 60P 4:3"
		, (1440, 30):"1920x1440 30P 4:3"
		, (1080, 60):"1920x1080 60P 16:9"
		, (1080, 30):"1920x1080 30P 16:9"
	}


	addr= None
	stopCB= None
	watchDog= False

	yi= None
	settings= None



	def __init__(self, addr=None, _stopCB=None):
		self.addr= addr or self.addr

		self.stopCB= callable(_stopCB) and _stopCB



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

		self.yi.cmd(Yi4kAPI.setSystemMode, 'record')
		self.yi.cmd(Yi4kAPI.setRecordMode, 'record_loop')
		self.yi.cmd(Yi4kAPI.setLoopDuration, '5 minutes')
		self.yi.cmd(Yi4kAPI.setVideoQuality, 'normal')
		self.yi.cmd(Yi4kAPI.setVideoStandard, 'NTSC')
		self.yi.cmd(Yi4kAPI.setVideoResolution, self.presets[yiFormat])

		res= self.yi.cmd(Yi4kAPI.startRecording)
		if res:
			logging.error('Starting error: %s' % res)
			self.yi.close()

			return

		self.yi.setCB('video_record_complete', self.canceled)
		self.watchDog= True


		logging.info('Started %s' % set(yiFormat))
		return True



#  todo 277 (Yi, clean) +0: remove recorded video files
	def stop(self, _stopRec=True):
		if not self.yi:
			logging.warning('Not started')
			return True #used also if externally stopped

		if not self.yi.sock:
			logging.error('Camera not found')
			return

		self.watchDog= False


		if _stopRec:
			res= self.yi.cmd(Yi4kAPI.stopRecording)
			if isinstance(res, int) and res<0:
				logging.error('Stopping error: %s' % res)
				return


		#restore settings
		#fallback if camera was in record already
		if self.settings:
			self.yi.cmd(Yi4kAPI.setVideoQuality, self.settings['video_quality'])
			self.yi.cmd(Yi4kAPI.setVideoStandard, self.settings['video_standard'])
			self.yi.cmd(Yi4kAPI.setVideoResolution, self.settings['video_resolution'])
			self.yi.cmd(Yi4kAPI.setVideoFieldOfView, self.settings['fov'])
			self.yi.cmd(Yi4kAPI.setLoopDuration, self.settings['loop_rec_duration'])
			self.yi.cmd(Yi4kAPI.setRecordMode, self.settings['rec_mode'])
			self.yi.cmd(Yi4kAPI.setSystemMode, self.settings['system_mode'])

		self.yi.close()
		self.yi= None


		logging.info('Finish')
		return True




	'''
	Camera stopped externally
	'''
	def canceled(self, _res):
		logging.info('Stopped event')
		threading.Timer(0, lambda: self.watchDog and self.stop(False)).start()
			
		self.stopCB and self.stopCB()
		
