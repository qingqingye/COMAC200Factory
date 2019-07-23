# import zmq
# from zmq.devices import monitored_queue
# from zhelpers import zpipe
import threading
import queue
from builtins import len
from multiprocessing import Process, Lock

class socketData():         #our data structure:{data,size,label}
	def __init__(self,data,size = 0,label = ""):
		self.data = data
		if (size <= 0):
			self.size = len(self.data)
		else:
			self.size = size
		self.label = label
		
	def set(self,data,size = 0,label = ""):#dict
		self.data = data
		self.size = size
		self.label = label

	def get(self): #get the structure
		return {"data":self.data,"size":self.size,"label":self.label}
	def getData(self): #get the structure
		return self.data
	def getSize(self): #get the structure
		return self.size
	def getLabel(self): #get the structure
		return self.label
	
	def isEmpty(self): #is empty?
		if (self.data == "" or self.size == 0):
			return 1
		else:
			return 0