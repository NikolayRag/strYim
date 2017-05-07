import Yi4kAPI
import logging


class YiControl():
	presets= {
		  (1440, 60):"1920x1440 60P 4:3"
		, (1440, 30):"1920x1440 30P 4:3"
		, (1080, 60):"1920x1080 60P 16:9"
		, (1080, 30):"1920x1080 30P 16:9"
	}


	addr= None

	yi= None
	settings= None


	def __init__(self, addr=None):
		self.addr= addr or self.addr



	'''
	_yiFormat is a (lines,fps)
	'''
	def start(self, _fps, _fmt):
		if self.yi:
			logging.error('Already started')
			return False

		yiFormat= (_fmt, _fps)
		if yiFormat not in self.presets:
			return False


# -todo 228 (Yi, fix) +0: detect Yi4kAPI errors: playback mode, busy switching
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

		return True


	def stop(self):
		if not self.yi:
			logging.error('Not started')
			return

		if not self.yi.sock:
			logging.error('Camera not found')
			return


		res= self.yi.cmd(Yi4kAPI.stopRecording)
		if isinstance(res, int) and res<0:
			logging.error('Stopping error: %s' % res)

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
