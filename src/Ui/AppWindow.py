from os import path

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

class Object():
	None



# -todo 239 (gui, feature) -1: make customizable destination list 

'''
Dragging window support
'''
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
	layout.camStates= {"Air":None, "Error":None, "Idle":None, 'Warn':None}
	layout.camMessages= {"Air":None, "Error":None, "Idle":None, 'Warn':None}
	layout.sinkStates= {"Air":None, "Error":None, "Idle":None, 'Warn':None}
	layout.sinkMessages= {"Air":None, "Error":None, "Idle":None, 'Warn':None}
	layout.play= None
#	layout.choose= None
#	layout.addSrc= None

	destCB= None
	playSourceCB= None
	playDestCB= None

	modulePath= path.abspath(path.dirname(__file__))



	def __init__(self):
		self.qApp = QApplication('')
		self.qApp.setStyle(QStyleFactory.create('plastique'))

		uiFile= path.join(self.modulePath,'AppWindow.ui')
		cMain= self.layout.main= QUiLoader().load(uiFile)


		#capture widgets
		self.layout.drag= cMain.findChild(QWidget, "outerFrame")


		self.layout.dest= cMain.findChild(QWidget, "editRtmpUrl")
		self.layout.stream= cMain.findChild(QWidget, "btnStreamGo")
		for state in self.layout.sinkMessages:
			self.layout.sinkMessages[state]= cMain.findChild(QWidget, ('labelSink'+state))
		for state in self.layout.sinkStates:
			self.layout.sinkStates[state]= cMain.findChild(QWidget, ('radioSink'+state))


#		self.layout.choose= cMain.findChild(QWidget, "btnOnCamera")
		self.layout.play= cMain.findChild(QWidget, "btnCamPlay")
		for state in self.layout.camMessages:
			self.layout.camMessages[state]= cMain.findChild(QWidget, ('labelCam'+state))
		for state in self.layout.camStates:
			self.layout.camStates[state]= cMain.findChild(QWidget, ('radioCam'+state))


#		self.layout.addSrc= cMain.findChild(QWidget, "btnAddSource")




		#update widgets state
		cMain.setWindowFlags(Qt.FramelessWindowHint)
		
		self.layout.drag.installEventFilter( QWinFilter(cMain) )


		for state in self.layout.sinkStates:
			self.sinkState(state)
		self.sinkState('Idle')

		for state in self.layout.camStates:
			self.camState(state)
		self.camState('Idle')


#  todo 241 (gui, feature) +0: add/remove sources
#		self.layout.choose.hide()
#		self.layout.addSrc.hide()


		self.layout.dest.textChanged.connect(self.changedDest)
		self.layout.play.toggled.connect(self.onPlaySource)
		self.layout.stream.toggled.connect(self.onPlayDest)



	'''
	Display UI and enter QT app loop
	'''
	def exec(self):
		#minimize window
		sizeAspect= self.layout.main.size().width()/self.layout.main.size().height()
		self.layout.main.resize(0,0)

		self.layout.main.show()


		self.qApp.exec_()



	def onPlaySource(self, _state):
		self.playSourceCB and self.playSourceCB(_state)


		
	def onPlayDest(self, _state):
		self.playDestCB and self.playDestCB(_state)



	def setSource(self, _playCB=None):
		self.playSourceCB= callable(_playCB) and _playCB



	def setDest(self, _dst=None, _changedCB=None, _playCB=None):
		self.playDestCB= callable(_playCB) and _playCB

# -todo 304 (ui, settings) +0: make updatable settings model
		oldCB= self.destCB
		self.destCB= None
		self.layout.dest.setText(_dst)
		self.destCB= oldCB

		if callable(_changedCB):
			self.destCB= _changedCB

	

	def changedDest(self, _val):
		self.destCB and self.destCB(_val)


#ui control


	'''
	Toggle camera state
	'''
	def camState(self, _state, _msg=''):
		self.layout.camStates[_state].toggle()

		if _msg:
			self.layout.camMessages[_state].setText(_msg)



	def sinkState(self, _state, _msg=''):
		self.layout.sinkStates[_state].toggle()

		if _msg:
			self.layout.sinkMessages[_state].setText(_msg)



	def btnPlaySource(self, _state):
		self.layout.play.setChecked(_state)



	def btnPlayDest(self, _state):
		self.layout.stream.setChecked(_state)
