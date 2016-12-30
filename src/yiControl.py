import time

from yi.yiAPI import *
from kiLog import *


class YiControl():
	presets= {"3840x2160 30P 16:9":'NTSC', "3840x2160 30P 16:9 super":'NTSC', "2560x1920 30P 4:3":'NTSC', "1920x1440 60P 4:3":'NTSC', "1920x1440 30P 4:3":'NTSC', "1920x1080 120P 16:9":'NTSC', "1920x1080 120P 16:9 super":'NTSC', "1920x1080 60P 16:9":'NTSC', "1920x1080 60P 16:9 super":'NTSC', "1920x1080 30P 16:9":'NTSC', "1920x1080 30P 16:9 super":'NTSC', "1280x960 120P 4:3":'NTSC', "1280x960 60P 4:3":'NTSC', "1280x720 240P 16:9":'NTSC', "1280x720 120P 16:9 super":'NTSC', "1280x720 60P 16:9 super":'NTSC', "840x480 240P 16:9":'NTSC'}


	settings= {}



	def __init__(self):
		None





	'''
	_yiFormat is a [setVideoStandard, setVideoResolution] list
	'''
	def start(self, _yiFormat, quality='normal'):
		if _yiFormat not in self.presets:
			return False


		yi= YiAPI()
		if yi.res==False:
			kiLog.err('Camera not found')
			return

		self.settings= yi.cmd(YiAPI.getSettings)

		yi.cmd(YiAPI.setSystemMode, 'record')
		yi.cmd(YiAPI.setRecordMode, 'record_loop')
		yi.cmd(YiAPI.setVideoQuality, quality)
		yi.cmd(YiAPI.setVideoStandard, self.presets[_yiFormat])
		yi.cmd(YiAPI.setVideoResolution, _yiFormat)

		yi.cmd(YiAPI.startRecording)

		yi.close()

		return True


	def stop(self):
		yi= YiAPI()
		if yi.res==False:
			kiLog.err('Camera not found')
			return

		res= yi.cmd(YiAPI.stopRecording)
#  todo 225 (Yi) +0: detect real command ending
		time.sleep(1.5)

		#restore settings
		yi.cmd(YiAPI.setSystemMode, self.settings['system_mode'])
		yi.cmd(YiAPI.setRecordMode, self.settings['rec_mode'])
		yi.cmd(YiAPI.setVideoQuality, self.settings['video_quality'])
		yi.cmd(YiAPI.setVideoStandard, self.settings['video_standard'])
		yi.cmd(YiAPI.setVideoResolution, self.settings['video_resolution'])
		yi.cmd(YiAPI.setVideoFieldOfView, self.settings['fov'])

		yi.close()
