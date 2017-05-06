import sys, os
def pyinstRoot(_relPath= ''):
	if '_MEIPASS' in dir(sys):
		root= sys._MEIPASS
	else:
		root= os.path.abspath(os.path.dirname(__file__))

	return os.path.join(root, _relPath)

