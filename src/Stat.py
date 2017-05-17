import time
import logging


class Stat():
	stat= None

	limit= 0


	'''
	Initialize Stat.
	Values stored are limited to 'limit' seconds.
	'''
	def __init__(self, limit=10):
		self.stat= []
		self.limit= limit



	def add(self, _val):
		if not isinstance(_val, (int,float)):
			logging.warning('Not a number added, skipped')
			return

		cTime= time.time()

		okN= 0
		for cStat in self.stat:
			if cStat[0] > (cTime -self.limit):
				break

			okN+= 1


		self.stat= self.stat[okN:]
		self.stat.append((cTime,_val))



	def min(self, limit=(0,1)):
		out= None
		for cVal in self.substat(limit):
			out= min(out or cVal[1], cVal[1])

		return out



	def max(self, limit=(0,1)):
		out= None
		for cVal in self.substat(limit):
			out= max(out or cVal[1], cVal[1])

		return out



	def last(self, limit=(0,1)):
		out= None		
		for cVal in self.substat(limit):
			out= cVal[1]
			break
			
		return out






	def substat(self, limit=(0,1)):
		cTime= time.time()

		stop= len(self.stat)
		start= stop

		for cVal in self.stat[::-1]:
			if cVal[0] < (cTime -limit[1]):
				break

			if cVal[0] > (cTime -limit[0]):
				start-= 1

			stop-= 1


		return self.stat[start:stop]
