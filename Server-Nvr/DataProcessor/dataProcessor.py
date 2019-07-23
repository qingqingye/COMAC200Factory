# coding=utf-8

from zmqyk.socketData import *
from zmqyk.socketReceiver import *
import base64
import json
import pytz
import time
import datetime
import numpy
import cv2
#from apitest import RandomNames
import requests
import sqlite3 as sql
from database import mylib
import numpy
from apscheduler.scheduler import Scheduler

timezone = pytz.timezone('Asia/Shanghai')
workersThroughGate = []
workersInRegion = [0,0,0,0,0,0,0,0]
workersInRegion1min=[0,0,0,0,0,0,0,0]
count =0
# faceRecUrl = "http://10.5.6.151:8080/mes/recognize"
# localip = "192.168.1.187"
faceRecUrl = 'http://192.168.3.222:5000/mes/recognize'
localip='192.168.3.254'




def TableHeatmap():
    global  workersInRegion1min
    global  count
    if count != 0 :
        workersInRegion1min = numpy.array(workersInRegion1min)//count
    path = 'C:\\Users\\24330\\Desktop\\Server-Nvr\\database\\info.db'
    conn = sql.connect(path)
    timeRecord = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    mylib.insert_heat(conn, workersInRegion1min[0] , workersInRegion1min[1], workersInRegion1min[2],
                                       workersInRegion1min[3], workersInRegion1min[4],
                                       workersInRegion1min[5], workersInRegion1min[6] , workersInRegion1min[7]),
    workersInRegion1min=[0,0,0,0,0,0,0,0]
    conn.commit()


sched = Scheduler()  # 实例化，固定格式
@sched.interval_schedule(seconds=60)  # 装饰器，seconds=60意思为该函数为1分钟运行一次
def mytask():
    TableHeatmap()
sched.start()  # 启动该脚本


def resolveFace(sdata):
    stringData = sdata.getData()
    stringLabel = str(sdata.getLabel(), 'utf-8')
    strjson = "".join([stringLabel.strip().rsplit("}", 1)[0], "}"])
    frameinfodata = json.loads(strjson, strict=False)

    streamid = frameinfodata['channel']

    cols = int(frameinfodata['width'])
    rows = int(frameinfodata['height'])

    imageRead = numpy.frombuffer(stringData, dtype=numpy.uint8)
    imageReshaped = imageRead.reshape([rows, cols, int(sdata.getSize() / rows / cols)])
    imageJpg = cv2.imencode('.jpg', imageReshaped)[1]

    base64_imgSrc = (base64.b64encode(imageJpg)).decode()

    base64_img = ''
    if (cols > rows):
        imageDecoded_t = imageReshaped[0:rows, int((cols - rows) / 2):int((cols + rows) / 2)]
        imageDecoded_t = cv2.resize(imageDecoded_t, (200, 200))
        base64_img = (base64.b64encode(cv2.imencode('.jpg', imageDecoded_t)[1])).decode()
        # cv2.imwrite("img_"+str(streamid)+".jpg",imageDecoded_t)
    else:
        imageDecoded_t = imageReshaped[int((rows - cols) / 2):int((cols + rows) / 2), 0:cols]
        imageDecoded_t = cv2.resize(imageDecoded_t, (200, 200))
        base64_img = (base64.b64encode(cv2.imencode('.jpg', imageDecoded_t)[1])).decode()

    base64_imgSrc = 'data:image/jpeg;base64,' + base64_imgSrc
    base64_img = 'data:image/jpeg;base64,' + base64_img

    worker = {}
    worker['wID'] = '100***'
    worker['name'] = 'ARJ21事业部'
    worker['title'] = ' '
    # worker['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    worker['time'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    worker['avatar'] = base64_img
    worker['avatartype'] = "base64"

    if (streamid == 0):
        # if(streamid == 10):
        worker['action'] = "in"
    else:
        worker['action'] = "out"

    try:
        jdata = {'image': base64_imgSrc}
        jheaders = {'Content-Type': 'application/json'}
        res = requests.request("post", faceRecUrl, headers=jheaders, data=json.dumps(jdata))
        bjdata = res.json()
        # print(bjdata)
        worker['wID'] = bjdata['result']['person']['id']
        worker['name'] = bjdata['result']['person']['name']
        worker['title'] = bjdata['result']['person']['title']
    except:
        print("recognize error!")

    return worker


def faceCallback(sdata):
    global workersThroughGate
    worker = resolveFace(sdata)
    
    isnew = True
    if(worker['wID'] != '100***'):
        for oworker in workersThroughGate:
            if(oworker['wID'] == worker['wID'] and oworker['action'] == worker['action']):
                isnew = False
                break

    if(isnew):
        if(len(workersThroughGate)>=10):
            workersThroughGate.pop(0)
        workersThroughGate.append(worker)

    print(len(workersThroughGate)," faces in buffer")

    path = 'C:\\Users\\24330\\Desktop\\Server-Nvr\\database\\info.db'
    conn = sql.connect(path)
    for i in workersThroughGate:
        changeFlag=1
        try:
            dbBack = mylib.select(conn,int(i['wID']),'gate_table')
            print(dbBack[0][2])
            if dbBack[0][2] ==i['action']:
                changeFlag=0
        except:
            pass
        if changeFlag==1:
            mylib.insert_gate(conn,i['wID'] ,i['name'],i['action'] )
            conn.commit()
    #   ['wID'], workerName=i['name'], action=i['action']

def regionCallback(sdata):
    global workersInRegion
    global  count
    global  workersInRegion1min
    #print("hahahahah")
    stringLabel=str(sdata.getLabel(),'utf-8')
    #print("Region str: ",stringLabel)
    strjson = "".join([stringLabel.strip().rsplit("}",1)[0],"}"])
    datainfo = json.loads(strjson,strict=False)
    WorkersNum =  int(datainfo['pc'])
    streamid = int(datainfo['streamIndex'])
    #print("Region: ",streamid,"pc: ",WorkersNum)

    if(streamid>3):
        streamid -= 1 
    streamid -= 1

    if(WorkersNum>workersInRegion[streamid]):
        workersInRegion[streamid]+=1
    elif(WorkersNum<workersInRegion[streamid]):
        workersInRegion[streamid]-=1

    workersInRegion1min = numpy.array(workersInRegion1min)+numpy.array(workersInRegion)
    count+=1


    

class DataProcessor():
    
    def __init__(self):
       
        self.regionReceivers =[]
        #self.workersThroughGate = []
        #self.workersInRegion = [0,0,0,0,0,0,0,0]
        self.area_titles = ['A','B','C','D','E','F','G','H']
        self.area_heat = [
            {
                "g":6.5,
                "l":3.25,
                "tmp":0
            },
            {
                "g":4.3,
                "l":1.5,
                "tmp":0
            },
            {
                "g":1.8,
                "l":5,
                "tmp":0
            },
            {
                "g":4.3,
                "l":5,
                "tmp":0
            },
            {
                "g":1.8,
                "l":1.5,
                "tmp":0
            },
            {
                "g":1.6,
                "l":3.25,
                "tmp":0
            },
            {
                "g":6.5,
                "l":5,
                "tmp":0
            },
            {
                "g":6.5,
                "l":1.5,
                "tmp":0
            }
        ]
        for i in range(1,9):
            pidx = i
            if(i>=3):
                pidx += 1 
            self.regionReceivers.append(socketReceiver("tcp://"+localip,str(15100+pidx)))
            self.regionReceivers[i-1].registerCallback(regionCallback)
            self.regionReceivers[i-1].startCallbacks()
        
        self.faceReceiverIn = socketReceiver("tcp://"+localip,"16000")
        self.faceReceiverIn.registerCallback(faceCallback)
        self.faceReceiverIn.startCallbacks()

        #self.faceReceiverOut = socketReceiver("tcp://"+localip,"16001")
        #self.faceReceiverOut.registerCallback(faceCallback)
        #self.faceReceiverOut.startCallbacks()

    def getWorkerCount(self,fid):
        global workersInRegion
        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        WorkersNum = 0

        """ sdata=self.regionReceiver.get()
        stringLabel=str(sdata.getLabel(),'utf-8')
		strjson = "".join([stringLabel.strip().rsplit("}",1)[0],"}"])
		datainfo=json.loads(strjson,strict=False)
		WorkersNum = datainfo['pc']
        streamid = datainfo['streamid'] """
        for num in workersInRegion:
            WorkersNum += num

        res_data['counter'] =  WorkersNum
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        rt_dic['result'] = res_data
        return rt_dic

    def getWorkerStatistic(self,fid):
        #global heatidx
        global workersInRegion
        rt_dic = {}
        res_data = {}
        res_areas = []
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"

        for i in range(0,8):
        # for area_name in area_titles:
            area = {}
            area['genre'] = self.area_titles[i] + '区'
            area['num'] = workersInRegion[i]
            res_areas.append(area)
            
        res_data['areas'] = res_areas
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        rt_dic['result'] = res_data
        return rt_dic

    def getHeatmap(self):
        global workersInRegion
        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        for i in range(0,8):
            self.area_heat[i]['tmp'] = workersInRegion[i]
        
        res_data['areas'] = self.area_heat
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        rt_dic['result'] = res_data
        return rt_dic

    def getGateInfoAsync(self):
        global workersThroughGate
        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        users = workersThroughGate.copy()
        #workersThroughGate.clear()
        res_data['users'] = users
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        rt_dic['result'] = res_data
        return rt_dic

    """
    def getGateInfo(self):
        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        users = []
        while (True):
            sdata =  self.faceReceiverIn.get()
            if (sdata.getSize() != 0):
                worker = resolveFace(sdata)
                users.append(worker)
            else:
                break
        while (True):
            sdata =  self.faceReceiverOut.get()
            if (sdata.getSize() != 0):
                worker = resolveFace(sdata)
                users.append(worker)
            else:
                break
        res_data['users'] = users
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        rt_dic['result'] = res_data
        return rt_dic
    """
   
        
    
