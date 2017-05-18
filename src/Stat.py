import time
import logging



'''
Collect value statistic over time.
'''
class Stat():
	stat= None

	limitGlobal= 0

	trigger= None


	'''
	Initialize Stat.
	Values stored are limited to 'limitGlobal' seconds.
	'''
	def __init__(self, limitGlobal=10):
		self.stat= []
		self.limitGlobal= limitGlobal



	def add(self, _val):
		if not isinstance(_val, (int,float)):
			logging.warning('Not a number added, skipped')
			return

		cTime= time.time()

		okN= 0
		for cStat in self.stat:
			if cStat[0] > (cTime -self.limitGlobal):
				break

			okN+= 1

		self.stat= self.stat[okN:]
		self.stat.append((cTime,_val))


		self.trigger and self.trigger.check()



	def min(self, limit=(0,1)):
		out= None
		for cVal in self.substat(limit):
			out= min(out or cVal[1], cVal[1])

		return out



	'''
	Define callback to trigger when value raise or fall over declared steps.
	'''
	def trigger(self, trigger):
		self.trigger= trigger



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



### PRIVATE


	'''
	Get subset of statistic over given time from now back to past, in seconds.
	'''
	def substat(self, limit=(0,1)):
		cTime= time.time()

		stop= len(self.stat)
		start= stop

		for cVal in self.stat[::-1]:
			if cVal[0] < (cTime -limit[1]):
				break

			if cVal[0] > (cTime -limit[0]):
				stop-= 1

			start-= 1


		return self.stat[start:stop]






class StatTrigger():
	triggerLimit= None
	triggerSteps= None
	triggerCB= None
	triggerDir= None
	triggerFn= None

	triggerLast= None


	def __init__(self, fn=None, limit=(0,1), steps=False, cb=False, direction=0):
		self.triggerFn= callable(fn) and fn
		self.triggerLimit= limit
		self.triggerSteps= (isinstance(steps, (set,list)) and steps) or [steps]
		self.triggerSteps.sort()
		self.triggerCB= callable(cb) and cb
		self.triggerDir= direction



	def check(self):
		_val= self.triggerFn(self.triggerLimit)

		if self.triggerLast!=None and _val!=None:
			if self.triggerDir>=0:
				for step in self.triggerSteps[::-1]:
					if (self.triggerLast < step) and (_val >= step):
						self.triggerCB(_val, True)
						break

			if self.triggerDir<=0:
				for step in self.triggerSteps:
					if (self.triggerLast > step) and (_val <= step):
						self.triggerCB(_val, False)
						break

		
		self.triggerLast= _val
