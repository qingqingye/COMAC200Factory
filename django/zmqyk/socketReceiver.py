import zmq
from zmq.devices import monitored_queue
# from zhelpers import zpipe
import threading
import queue
from multiprocessing import Process, Lock
from zmqyk.socketData import *

class socketReceiver(): #receiver for receiving data
	def __init__(self,address,port):
		self.address = address
		self.port = port
		context = zmq.Context()
		#self.socket = context.socket(zmq.DEALER)
		self.socket = context.socket(zmq.SUB)
		addp = self.address+":"+self.port
		print("socketReceiver receive from ",addp)
		#self.socket.bind(addp)
		self.socket.connect(addp)
		self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
		self.switch = 1
		self.queue = queue.Queue(5)   #we create a queue inside the socketReceiver object with a thread to receive data to fill in the queue
		self.funcList =[]   #fuList for each registerCallback function
		self.queueList =[]  #queueList for each registerCallback function
		self.threadList =[]   #threadList for each registerCallback function
		self.switchRegister = 1
		self.th1 = threading.Thread(target = socketReceiver.receive, args = (self,))
		self.th1.start()

		#self.sDataTmp = socketData("")

		print("socketReceiver initialized")
		# print("thread daemon",self.th1.daemon)

	""" def __del__(self):
		self.socket.disconnect() """

	def get(self):#get structure
		
		if (self.queue.empty() == 0):
			sData = self.queue.get()
			return sData
		else:
			sData = socketData("")
			return sData

	def registerCallback(self,function): #append function and queue
		self.funcList.append(function)
		self.queueList.append(queue.Queue(5))

	def startCallbacks(self): #start each thread for each callback function
		for i in range(0,len(self.funcList)):
			# print(i,self.funcList[i],self.queueList[i])
			thread = threading.Thread(target = socketReceiver.registerCallbackThread,args=(self,i, ))
			self.threadList.append(thread)
			self.threadList[i].start()

	def registerCallbackThread(self,index):
		while(self.switchRegister):
			sData = self.queueList[index].get()
			self.funcList[index](sData)

	def stopCallbacks(self):
		self.switchRegister = 0
		for eachThread in self.threadList:
			eachThread.join()

	def getConnectionState(self): #
		pass
	
	def receive(self): #use a thread for continuing receiving data
		# global queue
		# num = 0
		while (self.switch == 1):
			# print("in receivebyteMessage thread",self.queue.qsize())
			message = self.socket.recv()
			# print("message",message)
			""" try:
				data = message.decode()
				if (data == "ping\0"):
					# print("received ping!!send pong")
					self.socket.send(b"pong\0")
					continue
			except:
				pass
				#print("data[0:128]",data[0:128]) """
				

			
			if (self.queue.full() == 1):    #if full
				tdata = self.queue.get()
				del tdata
				# print(num," threadreceive queue full release one")
			sData=socketData(message[128:],len(message[128:]),message[0:127])	
			#self.sDataTmp = sData
			self.queue.put(sData)
			for eachQueue in self.queueList:
				if (eachQueue.full() == 1):    #if full
					tdata = eachQueue.get()
					del tdata
				eachQueue.put(sData)


	def stopReceiving(self):
		self.switch = 0
		self.th1.join()
