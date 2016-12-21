#  todo 120 (ui) +0: add ui

from .stryimLive import *


'''
Yi4k stream app.
Links three flows:
1. Camera live streaming
2. Camera state
3. UI
'''
class Stryim():
	live= StryimLive()



	@staticmethod
	def start(_dst):
		KiLog.states('', verb=True, ok=True)
		KiLog.states('Mp4Recover', verb=True, ok=True)
#		KiLog.states('MuxFLV', warn=False)

		#Yi4k camera constants
		MuxFLV.defaults(srate=48000)
		Stryim.selfIP= KiTelnet.defaults(address='192.168.42.1')

		Stryim.live.start('D:/yi/restore/stryim/L.flv', 30000./1001)



	@staticmethod
	def stop():
		Stryim.live.stop()
