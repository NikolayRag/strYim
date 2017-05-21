# =todo 120 (ui) +0: add ui
import Ui
from args import *



'''
Gui flow.
Stream can be restarted with different settings.
Camera is controlled constantly.
'''
if __name__ == '__main__':
	cArgs= Args(True)

	if cArgs.args:
		Ui.Ui(cArgs)
