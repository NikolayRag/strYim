import time

import Yi4kAPI
from kiLog import *


class YiControl():
	presets= {"3840x2160 30P 16:9":'NTSC', "3840x2160 30P 16:9 super":'NTSC', "2560x1920 30P 4:3":'NTSC', "1920x1440 60P 4:3":'NTSC', "1920x1440 30P 4:3":'NTSC', "1920x1080 120P 16:9":'NTSC', "1920x1080 120P 16:9 super":'NTSC', "1920x1080 60P 16:9":'NTSC', "1920x1080 60P 16:9 super":'NTSC', "1920x1080 30P 16:9":'NTSC', "1920x1080 30P 16:9 super":'NTSC', "1280x960 120P 4:3":'NTSC', "1280x960 60P 4:3":'NTSC', "1280x720 240P 16:9":'NTSC', "1280x720 120P 16:9 super":'NTSC', "1280x720 60P 16:9 super":'NTSC', "840x480 240P 16:9":'NTSC'}


	settings= {}



	@staticmethod
	def defaults(ip):
		if ip:
			Yi4kAPI.YiAPI.defaults(ip=ip)

			
	def __init__(self):
		None





	'''
	_yiFormat is a [setVideoStandard, setVideoResolution] list
	'''
	def start(self, _yiFormat, quality='normal'):
		if _yiFormat not in self.presets:
			return False


# -todo 228 (Yi, fix) +0: detect Yi4kAPI errors: playback mode, busy switching
		yi= Yi4kAPI.YiAPI()
		if yi.res==False:
			kiLog.err('Camera not found')
			return

		self.settings= yi.cmd(Yi4kAPI.getSettings)

		yi.cmd(Yi4kAPI.setSystemMode, 'record')
		yi.cmd(Yi4kAPI.setRecordMode, 'record_loop')
		yi.cmd(Yi4kAPI.setLoopDuration, '5 minutes')
		yi.cmd(Yi4kAPI.setVideoQuality, quality)
		yi.cmd(Yi4kAPI.setVideoStandard, self.presets[_yiFormat])
		yi.cmd(Yi4kAPI.setVideoResolution, _yiFormat)

		time.sleep(1)
		yi.cmd(Yi4kAPI.startRecording)

		yi.close()

		return True


	def stop(self):
		yi= Yi4kAPI.YiAPI()
		if yi.res==False:
			kiLog.err('Camera not found')
			return

# =todo 230 (Yi) +0: detect error when stopping stopped cam
		res= yi.cmd(Yi4kAPI.stopRecording)
#  todo 225 (Yi) +0: detect real command ending
		time.sleep(2)

		#restore settings
		yi.cmd(Yi4kAPI.setVideoQuality, self.settings['video_quality'])
		yi.cmd(Yi4kAPI.setVideoStandard, self.settings['video_standard'])
		yi.cmd(Yi4kAPI.setVideoResolution, self.settings['video_resolution'])
		yi.cmd(Yi4kAPI.setVideoFieldOfView, self.settings['fov'])
		yi.cmd(Yi4kAPI.setLoopDuration, self.settings['loop_rec_duration'])
		yi.cmd(Yi4kAPI.setRecordMode, self.settings['rec_mode'])
		yi.cmd(Yi4kAPI.setSystemMode, self.settings['system_mode'])

		yi.close()
