'''
Agent flow:

* loop record
	* detect file being recorded
	* read tail till end
		* split 264/AAC
		* make Atoms available to read from socket 
'''
class YiAgent():
	def __init__(self):
		print(1+1)
