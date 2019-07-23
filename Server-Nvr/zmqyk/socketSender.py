import zmq
from zmq.devices import monitored_queue
# from zhelpers import zpipe
import threading
import queue
from multiprocessing import Process, Lock
from zmqyk.socketData import *

class socketSender(): #sender for sending data
	def __init__(self,address,port):
		self.address = address	
		self.port = port
		context = zmq.Context()
		#self.socket = context.socket(zmq.DEALER)
		self.socket = context.socket(zmq.PUB)
		addp = self.address+":"+self.port
		#self.socket.connect(self.addp)
		self.socket.bind(addp)

	""" def __del__(self):
		self.socket.disconnect() """

	def send(self,struct): #send socketdata
		# if (struct.getLabel() == "message"):
		# 	jsonmessage = json.dumps(struct.get())
		# 	jsonmessageEnd = jsonmessage+"\0"
		# 	self.socket.send(jsonmessageEnd.encode())
		data = struct.getData()
		label = struct.getLabel()
		size = struct.getSize()
		labeljust = label.ljust(128,'\x00')
		# print("labeljust",labeljust)
		# if label=="picture":
		message = labeljust.encode()+bytes(data)
		#print("dataSize=  ",size)
		# print("dataEn =  ",len(dataEn))
		# print("messageBytes =  ",len(labeljust.encode())," + ",len(dataByte))
		#print("messageBytes =  ",len(message))
		# print("time ",time.asctime( time.localtime(time.time()) ))
		self.socket.send(message)
		# elif label=="???":
		# 	pass
		# else:
		# 	print("cant send the message with this type")
		# print("Error we can send the message of this type!")
	def getConnectionState(self): #use ping-pong to check connection state
		""" for i in range(10):
			self.socket.send(b"ping\0")
		print("send ping 10times")
		messageEncode = None
		for i in range(1,10000):      #try to receive 10 times for testing connection
			# print(i)
			try:
				messageEncode = self.socket.recv(zmq.DONTWAIT)
				# print(i,"jsonmessage",jsonmessage)
				message = messageEncode.decode()
				print(message, message=="pong\0")
				if (message == "pong\0"):
					return True
			except:
				pass
		return False """
		pass