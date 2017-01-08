from os import path

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
#from PySide.QtDeclarative import QDeclarativeView



class QWinFilter(QObject):
	mouseOffset= None

	def __init__(self, _base):
		super().__init__(_base)


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



class Gui():
	camStates= ["Air", "Ready", "Idle", "Error", "None"]

	qApp= None
	qMain= None
	qCamState= None


	modulePath= path.abspath(path.dirname(__file__))

	def __init__(self):
		self.qApp = QApplication('')
		self.qApp.setStyle(QStyleFactory.create('plastique'))

		uiFile= path.join(self.modulePath,'stryim.ui')
		self.qMain= QUiLoader().load(uiFile)

		self.qMain.setWindowFlags(Qt.FramelessWindowHint)
		self.qMain.installEventFilter( QWinFilter(self.qMain) )


		#update widgets state

		self.qMain.findChild(QWidget, "btnCamStop").hide()

		self.qCamState= {}
		for state in self.camStates:
			self.qCamState[state]= self.qMain.findChild(QWidget, ('radioCam'+state))
			self.camState(state)
		self.camState('None')
		


#		self.qMain= QDeclarativeView()
#		self.qMain.setSource(QUrl( os.path.join(self.modulePath,'stryim.qml') ))
#		self.qMain.show()


	'''
	Display UI and enter QT app loop
	'''
	def exec(self):
		#minimize window
		sizeAspect= self.qMain.size().width()/self.qMain.size().height()
		self.qMain.resize(0,0)

		self.qMain.show()

		#restore explicit aspect
		cSize= self.qMain.size()
		cSize.setWidth(cSize.height()*sizeAspect)
		cSize.setHeight(cSize.width()/sizeAspect)
		self.qMain.resize(cSize)


		self.qApp.exec_()



	'''
	Toggle camera state
	'''
	def camState(self,_state):
		self.qCamState[_state].toggle()

