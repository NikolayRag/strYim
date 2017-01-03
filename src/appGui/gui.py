import os

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import QDeclarativeView

class gui():
	QApp= None
	view= None

	modulePath= os.path.relpath(os.path.dirname(__file__))

	def __init__(self):
		self.QApp = QApplication('')
		self.QApp.setStyle(QStyleFactory.create('plastique'))

		self.view= QDeclarativeView()
		self.view.setSource(QUrl( os.path.join(self.modulePath,'stryim.qml') ))
		self.view.show()


	def exec(self):
		self.QApp.exec_()
