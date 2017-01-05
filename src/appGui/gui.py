from os import path

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
#from PySide.QtDeclarative import QDeclarativeView

class gui():
	QApp= None
	view= None

	modulePath= path.abspath(path.dirname(__file__))

	def __init__(self):
		self.QApp = QApplication('')
		self.QApp.setStyle(QStyleFactory.create('plastique'))

		uiFile= path.join(self.modulePath,'stryim.ui')
		self.view= QUiLoader().load(uiFile)
		self.view.setWindowFlags(Qt.FramelessWindowHint)

		self.view.findChild(QWidget, "btnCamStop").hide()
		self.view.findChild(QWidget, "radioCamAir").toggle()
		self.view.findChild(QWidget, "radioCamReady").toggle()
		self.view.findChild(QWidget, "radioCamIdle").toggle()
		self.view.findChild(QWidget, "radioCamError").toggle()
		self.view.findChild(QWidget, "radioCamNone").toggle()
		


#		self.view= QDeclarativeView()
#		self.view.setSource(QUrl( os.path.join(self.modulePath,'stryim.qml') ))
#		self.view.show()

	def exec(self):
		self.view.show()

		self.QApp.exec_()
