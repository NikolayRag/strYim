#  todo 261 (YiAgent, check) +0: set camera settings

from .Yi4k import *

Yi4kPresets= {
		(1080, 25): {
			'yiRes': '1920x1080 25P 16:9',
			'yiStd': 'PAL',
			'fps': 25,
			'header': [
			]
		},
		(1080, 30): {
			'yiRes': '1920x1080 30P 16:9',
			'yiStd': 'NTSC',
			'fps': 30000/1001,
			'header': [
				b'\'M@3\x9ad\x03\xc0\x11?,\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea`\xe8`\x00\xb7\x18\x00\x02\xdcl\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00[\x8d\x97ypxD"R\xc0'
				, b'\x28\xee\x38\x80'
			]
		},
		(1440, 25): {
			'yiRes': '1920x1440 25P 4:3',
			'yiStd': 'PAL',
			'fps': 25,
			'header': [
			]
		},
		(1440, 30): {
			'yiRes': '1920x1440 30P 4:3',
			'yiStd': 'NTSC',
			'fps': 30000/1001,
			'header': [
			]
		}
}
