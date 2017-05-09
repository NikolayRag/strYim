import sys, os

ROOT= os.path.abspath(os.path.dirname(__file__))
if '_MEIPASS' in dir(sys):
	ROOT= sys._MEIPASS
