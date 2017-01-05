from os import path

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
#from PySide.QtDeclarative import QDeclarativeView



class QWinFilter(QObject):
	mouseOffset= None

	def eventFilter(self, obj, event):
		if event.type()==QEvent.MouseButtonPress:
			self.mouseOffset= event.globalPos()-obj.window().pos()
			return True

		if event.type()==QEvent.MouseButtonRelease:
			self.mouseOffset= False
			return True

		if event.type()==QEvent.MouseMove and self.mouseOffset:
			obj.window().move(event.globalPos()-self.mouseOffset)
			return True


		try:
			return QObject.eventFilter(self, obj, event)
		except:
			return False



class gui():
	qApp= None
	qMain= None



	modulePath= path.abspath(path.dirname(__file__))

	def __init__(self):
		self.qApp = QApplication('')
		self.qApp.setStyle(QStyleFactory.create('plastique'))

		uiFile= path.join(self.modulePath,'stryim.ui')
		self.qMain= QUiLoader().load(uiFile)

		self.qMain.setWindowFlags(Qt.FramelessWindowHint)
		self.qMain.installEventFilter( QWinFilter(self.qMain) )


		self.qMain.findChild(QWidget, "btnCamStop").hide()
		self.qMain.findChild(QWidget, "radioCamAir").toggle()
		self.qMain.findChild(QWidget, "radioCamReady").toggle()
		self.qMain.findChild(QWidget, "radioCamIdle").toggle()
		self.qMain.findChild(QWidget, "radioCamError").toggle()
		self.qMain.findChild(QWidget, "radioCamNone").toggle()
		


#		self.qMain= QDeclarativeView()
#		self.qMain.setSource(QUrl( os.path.join(self.modulePath,'stryim.qml') ))
#		self.qMain.show()

	def exec(self):
		self.qMain.show()

		self.qApp.exec_()
