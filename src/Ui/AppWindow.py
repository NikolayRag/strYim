from os import path

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

class Object():
	None



# -todo 239 (gui, feature) +0: make customizable destination list 

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

		return False




class AppWindow():
	qApp= None

	layout= Object()
	layout.main= None
	layout.drag= None
	layout.dest= None
	layout.stream= None
	layout.camStates= {"Air":None, "Ready":None, "Idle":None, "Error":None, "None":None}
	layout.play= None
	layout.choose= None
	layout.addSrc= None

	playCB= None
	streamCB= None
	destCB= None

	modulePath= path.abspath(path.dirname(__file__))



	def __init__(self, _playCB=None, _streamCB=None, _destCB=None):
		self.playCB= _playCB
		self.streamCB= _streamCB
		self.destCB= _destCB


		self.qApp = QApplication('')
		self.qApp.setStyle(QStyleFactory.create('plastique'))

		uiFile= path.join(self.modulePath,'stryim.ui')
		cMain= self.layout.main= QUiLoader().load(uiFile)


		#capture widgets
		self.layout.drag= cMain.findChild(QWidget, "outerFrame")


		self.layout.dest= cMain.findChild(QWidget, "editRtmpUrl")
		self.layout.stream= cMain.findChild(QWidget, "btnStreamGo")


		self.layout.choose= cMain.findChild(QWidget, "btnOnCamera")
		self.layout.play= cMain.findChild(QWidget, "btnCamPlay")
		for state in self.layout.camStates:
			self.layout.camStates[state]= cMain.findChild(QWidget, ('radioCam'+state))


		self.layout.addSrc= cMain.findChild(QWidget, "btnAddSource")




		#update widgets state
		cMain.setWindowFlags(Qt.FramelessWindowHint)
		
		self.layout.drag.installEventFilter( QWinFilter(cMain) )


		for state in self.layout.camStates:
			self.camState(state)
		self.camState('None')


#  todo 241 (gui, feature) +0: add/remove sources
		self.layout.choose.hide()
		self.layout.addSrc.hide()


		if callable(_destCB):
			self.layout.dest.textChanged.connect(_destCB)




	'''
	Display UI and enter QT app loop
	'''
	def exec(self):
		#minimize window
		sizeAspect= self.layout.main.size().width()/self.layout.main.size().height()
		self.layout.main.resize(0,0)

		self.layout.main.show()


		self.qApp.exec_()



	'''
	Toggle camera state
	'''
	def camState(self, _state):
		self.layout.camStates[_state].toggle()



	def destination(self, _dst):
		self.layout.dest.setText(_dst)
