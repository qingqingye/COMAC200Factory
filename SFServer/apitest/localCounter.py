import threading
import time

class FrameCounter(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.isneedBack = False
        self.isneedFor = False
        self.isneedReset = False
        self.isRun = True
        self.frameid = 0
        self.maxframeid = 3600

    def run(self):

        while(self.isRun):
            self.frameid += 1
            if(self.isneedReset):
                self.frameid = 0
                self.isneedReset = False
            if(self.isneedBack):
                self.frameid -= 20
                if(self.frameid < 0):
                    self.frameid = 0
                self.isneedBack = False
            if(self.isneedFor):
                self.frameid += 20
                if(self.frameid > self.maxframeid):
                    self.frameid = self.maxframeid
                self.isneedFor = False
            if(self.frameid > self.maxframeid):
                self.frameid = 0
            time.sleep(0.1)

    def reset(self):
        self.isneedReset = True

    def backward(self):
        self.isneedBack = True

    def forward(self):
        self.isneedFor = True

    def getFrameID(self):
        return self.frameid

    def stop(self):
        self.isRun = False
        self.join()