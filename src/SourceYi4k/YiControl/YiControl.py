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

	settings= None


	def __init__(self, addr=None):
		self.addr= addr or self.addr



	'''
	_yiFormat is a (lines,fps)
	'''
	def start(self, _fps, _fmt):
		yiFormat= (_fmt, _fps)
		if yiFormat not in self.presets:
			return False


# -todo 228 (Yi, fix) +0: detect Yi4kAPI errors: playback mode, busy switching
		yi= Yi4kAPI.YiAPI(self.addr)
		if not yi.sock:
			logging.error('Camera not found')
			return

		self.settings= yi.cmd(Yi4kAPI.getSettings)

		yi.cmd(Yi4kAPI.setSystemMode, 'record')
		yi.cmd(Yi4kAPI.setRecordMode, 'record_loop')
		yi.cmd(Yi4kAPI.setLoopDuration, '5 minutes')
		yi.cmd(Yi4kAPI.setVideoQuality, 'normal')
		yi.cmd(Yi4kAPI.setVideoStandard, 'NTSC')
		yi.cmd(Yi4kAPI.setVideoResolution, self.presets[yiFormat])

		yi.cmd(Yi4kAPI.startRecording)

		yi.close()

		return True


	def stop(self):
		yi= Yi4kAPI.YiAPI(self.addr)
		if not yi.sock:
			logging.error('Camera not found')
			return

# =todo 230 (Yi) +0: detect error when stopping stopped cam
		res= yi.cmd(Yi4kAPI.stopRecording)

		#restore settings
		#fallback if camera was in record already
		if self.settings:
			yi.cmd(Yi4kAPI.setVideoQuality, self.settings['video_quality'])
			yi.cmd(Yi4kAPI.setVideoStandard, self.settings['video_standard'])
			yi.cmd(Yi4kAPI.setVideoResolution, self.settings['video_resolution'])
			yi.cmd(Yi4kAPI.setVideoFieldOfView, self.settings['fov'])
			yi.cmd(Yi4kAPI.setLoopDuration, self.settings['loop_rec_duration'])
			yi.cmd(Yi4kAPI.setRecordMode, self.settings['rec_mode'])
			yi.cmd(Yi4kAPI.setSystemMode, self.settings['system_mode'])

		yi.close()
