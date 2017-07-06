import Yi4kAPI
import threading, re
import logging


'''
Put camera in mode suitable for capturing stream.

Record is started with specified settings, which are restored
 after record is done.
'''
class YiControl():
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
	_preset is defined in Yi4kModule
	'''
	def start(self, _preset, _flat=False):
		if self.started:
			logging.warning('Already started')
			return


		self.yi= Yi4kAPI.YiAPI(self.addr)
		if not self.yi.sock:
			logging.error('Camera not found')
			return
		self.started= True


		self.settings= self.yi.cmd(Yi4kAPI.getSettings)

		if _flat:
			resA= [
				  self.yi.cmd(Yi4kAPI.setRecordMode, 'record')
			]
		else:
			resA= [
				  self.yi.cmd(Yi4kAPI.setRecordMode, 'record_loop')
				, self.yi.cmd(Yi4kAPI.setLoopDuration, '5 minutes')
			]
		resA.extend([
			  self.yi.cmd(Yi4kAPI.setVideoQuality, 'normal')
			, self.yi.cmd(Yi4kAPI.setVideoStandard, _preset['yiStd'])
			, self.yi.cmd(Yi4kAPI.setVideoResolution, _preset['yiRes'])
		])
		logging.info('Set to: %s' % resA)

		res= self.yi.cmd(Yi4kAPI.startRecording)
		if res:
			logging.error('Starting error: %s' % res)
			self.yi.close()
			self.started= False

			return

		self.yi.setCB('video_record_complete', self.stopped)


		logging.info('Started %s' % _preset['yiRes'])
		return True



	def stop(self):
		if not self.started:
			logging.info('Not started')
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
	Restore settings and close YiAPI
	'''
	def reset(self):
		if self.settings:
			resA= [
				  self.yi.cmd(Yi4kAPI.setVideoQuality, self.settings['video_quality'])
				, self.yi.cmd(Yi4kAPI.setVideoStandard, self.settings['video_standard'])
				, self.yi.cmd(Yi4kAPI.setVideoResolution, self.settings['video_resolution'])
				, self.yi.cmd(Yi4kAPI.setLoopDuration, self.settings['loop_rec_duration'])
				, self.yi.cmd(Yi4kAPI.setRecordMode, self.settings['rec_mode'])
			]
			logging.info('Reset to: %s' % resA)


		self.yi.close()
