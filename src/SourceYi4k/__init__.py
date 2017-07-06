#  todo 261 (YiAgent, check) +0: set camera settings

from .Yi4k import *

Yi4kPresets= {
		(1080, 25): {
			'yiRes': '1920x1080 25P 16:9',
			'yiStd': 'PAL',
			'fps': 25,
			'headerA': [
			]
		},
		(1080, 30): {
			'yiRes': '1920x1080 30P 16:9',
			'yiStd': 'NTSC',
			'fps': 30000/1001,
			'headerA': [
			]
		},
		(1440, 25): {
			'yiRes': '1920x1440 25P 4:3',
			'yiStd': 'PAL',
			'fps': 25,
			'headerA': [
			]
		},
		(1440, 30): {
			'yiRes': '1920x1440 30P 4:3',
			'yiStd': 'NTSC',
			'fps': 30000/1001,
			'headerA': [
			]
		}
}
