from django.shortcuts import render
# coding:utf-8
from django.http import HttpResponse
import json
import datetime
import pytz
from factorymodel.models import *
import requests
from zmqyk.socketData import *
from zmqyk.socketReceiver import *
import base64
import datetime
import numpy
import cv2
from django.db.models import Count
from django.contrib.auth.models import User, Group
import math

timezone = pytz.timezone('Asia/Shanghai')
count=0
workersThroughGate = []
workersInRegion = [0,0,0,0,0,0,0,0]
workersInRegion1min=[0,0,0,0,0,0,0,0]
avgRate=0
#faceRecUrl = "http://19x.xxx.xxx.xxx/mes/recognize"
faceRecUrl = 'http://192x.xxx.xxx.xxx/mes/recognize'
weblip='192.xx.xxx.x'
localip = "192.xx.xx.x"
# faceRecUrl = "http://10.xx.xxmes/recognize"
# localip = "192.xx.xx.xx"


def TableGate():
    global workersThroughGate
    users = workersThroughGate.copy()
    for i in users:
        #print(i['wID'],i['action'])
        #print(i.workerId,i.action)
        creatFlag = 1  # when it=0 means ,he has been recorded 'in' and still in area don't need recorded again
        try:
            lateastRecord = gatelog_table.objects.filter(workerName=i['name']).order_by('-time')[0]
            if (lateastRecord.action == i['action']):  # if the lateast action is the same as new action
                creatFlag = 0
        except:
            pass

        if creatFlag == 1:
            gatelog_table.objects.create(workerId=i['wID'], workerName=i['name'], action=i['action'])
    #  user :'wID': '0', 'name': '', 'title': '工程师', 'time': '2019-04-16 12:37:59', 'avatar': 'avatartype': 'base64', 'action': 'in'
    print('gatetable new')


def TableHeatmap():
    global workersInRegion1min
    global count
    print(count,'count')
    workersInRegion1min = numpy.array(workersInRegion1min)//count
    count=0
    for i in workersInRegion1min:
        print(i)
    heatmap_table.objects.create(
        A=workersInRegion1min[0],
        B=workersInRegion1min[1],
        C=workersInRegion1min[2],
        D=workersInRegion1min[3],
        E=workersInRegion1min[4],
        F=workersInRegion1min[5],
        G=workersInRegion1min[6],
        H=workersInRegion1min[7])
    print('heatmaptable new')



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
    # worker['action'] = "in"

    if (streamid == 0):
        # if(streamid == 10):
        worker['action'] = "in"
    else:
        worker['action'] = "out"

    # print("Face receive image: ",frameid,"_",faceindex,"_",worker['action'])

    # print(res.json())
    # rctt = "".join(res.content).encode('utf-8').strip()
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
    if(str(worker['wID']) != '100***'):
        for oworker in workersThroughGate:
            if(str(oworker['wID']) == str(worker['wID']) and str(oworker['action']) == str(worker['action'])):
                isnew = False
                break

    if(isnew):
        if(len(workersThroughGate)>=10):
            workersThroughGate.pop(0)
        workersThroughGate.append(worker)

    TableGate()
    print(len(workersThroughGate)," faces in buffer")


def regionCallback(sdata):
    global workersInRegion1min
    global workersInRegion
    global  count
    stringLabel = str(sdata.getLabel(), 'utf-8')
    # print("Region str: ",stringLabel)
    strjson = "".join([stringLabel.strip().rsplit("}", 1)[0], "}"])
    datainfo = json.loads(strjson, strict=False)
    WorkersNum = int(datainfo['pc'])
    streamid = int(datainfo['streamIndex'])
    # print("Region: ",streamid,"pc: ",WorkersNum)

    if (streamid > 3):
        streamid -= 1
    streamid -= 1

    if (WorkersNum > workersInRegion[streamid]):
        workersInRegion[streamid] += 1
    elif (WorkersNum < workersInRegion[streamid]):
        workersInRegion[streamid] -= 1

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


        for i in range(1,10):
            pidx = i
            if(i>=3):
                pidx += 1
            self.regionReceivers.append(socketReceiver("tcp://"+ weblip ,str(15100+pidx)))
            self.regionReceivers[i-1].registerCallback(regionCallback)
            self.regionReceivers[i-1].startCallbacks()

        self.faceReceiverIn = socketReceiver("tcp://"+localip,"XXXX")
        self.faceReceiverIn.registerCallback(faceCallback)
        self.faceReceiverIn.startCallbacks()

        self.faceReceiverOut = socketReceiver("tcp://"+localip,"xxxxxx")
        self.faceReceiverOut.registerCallback(faceCallback)
        self.faceReceiverOut.startCallbacks()


        self.thereDmapReceiver = socketReceiver("tcp://localhost","xxxxx")



    def getWorkerCount(self,request):
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
        return HttpResponse(json.dumps(rt_dic,ensure_ascii=False),content_type="application/json,charset=utf-8")

    def getWorkerStatistic(self,request):
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
        return HttpResponse(json.dumps(rt_dic, ensure_ascii=False), content_type="application/json,charset=utf-8")

    def getHeatmap(self,request):
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
        return HttpResponse(json.dumps(rt_dic,ensure_ascii=False),content_type="application/json,charset=utf-8")

    def getGateInfoAsync(self,request):
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
        return HttpResponse(json.dumps(rt_dic,ensure_ascii=False),content_type="application/json,charset=utf-8")



    def getGateInfo(self,request):
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
        return HttpResponse(json.dumps(rt_dic,ensure_ascii=False),content_type="application/json,charset=utf-8")



    def thereDcam(self,request):
        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"


        while(True):
            sdata =  self.thereDmapReceiver.get()
            if (sdata.getSize() != 0):
                print('yes')
                stringLabel = str(sdata.getLabel(), 'utf-8')
                strjson = "".join([stringLabel.strip().rsplit("}", 1)[0], "}"])
                datainfo = json.loads(strjson, strict=False)
                PointNum = int(datainfo['PointNum'])
                TriCamid = int(datainfo['TriCamID'])
                stringData = sdata.getData()
                array = numpy.frombuffer(stringData, dtype=numpy.float32)
                print(PointNum, TriCamid, array)
                break
            else:
                array=[1,2,3]
                break

        rt_dic['result'] = str(array)
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        return HttpResponse(json.dumps(rt_dic,ensure_ascii=False),content_type="application/json,charset=utf-8")


    def tableGate(self,request):
        global workersThroughGate
        users = workersThroughGate.copy()
        for i in users:
            print(i['name'])
            creatFlag = 1 # when it=0 means ,he has been recorded 'in' and still in area don't need recorded again
            try :
                lateastRecord = gatelog_table.objects.filter(workerName=i['name']).order_by('-time')[0]
                if(lateastRecord.action == i['action'] ):  #if the lateast action is the same as new action
                    creatFlag = 0
            except:
                pass

            if creatFlag ==1:
                gatelog_table.objects.create(workerId=i['wID'], workerName=i['name'], action=i['action'] )

    #  user :'wID': '0', 'name': '', 'title': '工程师', 'time': '2019-04-16 12:37:59', 'avatar': 'avatartype': 'base64', 'action': 'in'

        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        return HttpResponse(json.dumps(rt_dic, ensure_ascii=False), content_type="application/json,charset=utf-8")


    def tableHeatmap(self ,requests):
        global workersInRegion
        for i in workersInRegion:
            print(i)
        heatmap_table.objects.create(
        A = workersInRegion[0],
        B = workersInRegion[1],
        C = workersInRegion[2],
        D = workersInRegion[3],
        E = workersInRegion[4],
        F = workersInRegion[5],
        G = workersInRegion[6],
        H = workersInRegion[7])
        rt_dic = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        return HttpResponse(json.dumps(rt_dic, ensure_ascii=False), content_type="application/json,charset=utf-8")




    def hositoryReturn(self,requests):
        dateStr = requests.GET['date']
        today = datetime.datetime.now(timezone).strftime('%Y/%m/%d')
        datedate=dateStr.split('/')
        mth = datedate[1]
        day = datedate[2]
        print(day,mth,"day ,mth")


        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        rt_dic["result"] = res_data
        users = []

        history = gatelog_table.objects.filter(time__day=day ,time__month=mth)
        for i in history:
            user = {}
            user['id']=i.workerId
            user['name']=i.workerName
            user['action']=i.action

            users.append(user)
            print(i.workerId, i.workerName, i.action,i.time)
        # workersThroughGate.clear()
        res_data['users'] = users
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        rt_dic['result'] = res_data
        return HttpResponse(json.dumps(rt_dic, ensure_ascii=False), content_type="application/json,charset=utf-8")



    def ratePross(self,today,today_list,dateStr):
        table = []
        allRate=0
        msgS = today_list.values_list('workerName').annotate(Count('id'),)
        count=1
        for i in msgS:   #give every person's history to web

            print(i[0],i[1],'name time')
            logNum=i[1]
            personLog = today_list.filter(workerName=i[0])


            user = {}
            user["key"] = count
            count += 1
            user["name"] = i[0]
            user["id"]=personLog[0].workerId
            if personLog[0].action=="out":
                user["stayTime"]=user["bigTime"]=user["workRate"]="out before in"

            else:    # has the right record first in
                now = datetime.datetime.now()
                d2 = datetime.datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                lateastRecord = personLog.order_by('-time')[0].time
                if today==dateStr:  #watch today's workrate
                    bigTime=d2-personLog[0].time   #time now - first in time
                    user['bigtime'] = str(bigTime)
                    stayTime = 0
                    if logNum % 2 == 0:  # if log num is even means he is out now
                        stayTime = personLog[logNum - 1].time - personLog[logNum - 2].time
                        flag = logNum - 3
                    else:  # if it's odd means he is in now
                        stayTime = d2 - personLog[logNum - 1].time
                        flag = logNum - 2
                    while flag > 0:
                        stayTime += personLog[flag].time - personLog[flag - 1].time
                        flag -= 2
                    user["stayTime"] = str(stayTime)[:-3]
                    user['workRate'] = stayTime / bigTime
                    allRate += stayTime / bigTime

                else:  # watch day before
                    bigTime=lateastRecord-personLog[0].time
                    print(bigTime,lateastRecord,personLog[0].time,"time")
                    user['bigtime'] = str(bigTime)[:-3]
                    stayTime = 0
                    if logNum % 2 == 0:  # if log num is even means he is out now
                        stayTime = personLog[logNum - 1].time - personLog[logNum - 2].time
                        flag = logNum - 3
                        while flag > 0:
                            stayTime += personLog[flag].time - personLog[flag - 1].time
                            flag -= 2
                        user["stayTime"] = str(stayTime)
                        user['workRate'] = stayTime / bigTime
                        allRate += stayTime / bigTime
                    else:   # if log num is odd, it's ilegal
                        user["stayTime"]=user["bigTime"]=user["workRate"]="has no get off work infor"

            table.append(user)

        averageRate = allRate/len(msgS)

        return(table,averageRate)




    def workrate(self,requests):
        dateStr = requests.GET['date']
        today = datetime.datetime.now(timezone).strftime('%Y/%m/%d')
        datedate=dateStr.split('/')
        mth = datedate[1]
        day = datedate[2]
        print(day,mth,"day ,mth")

        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        rt_dic["result"]=res_data
        table = []
        allRate=0
        today_list = gatelog_table.objects.filter(time__day=day, time__month=mth)
        msgS = today_list.values_list('workerName').annotate(Count('id'),)
        print(msgS)
        count=1
        for i in msgS:   #give every person's history to web

            print(i[0],i[1])
            logNum=i[1]
            personLog = today_list.filter(workerName=i[0])
            for j in personLog:
                print(j.workerName,j.workerId,j.time,j.action)

            user = {}
            user["key"] = count
            count += 1
            user["name"] = i[0]
            user["id"]=personLog[0].workerId
            if personLog[0].action=="out":
                user["stayTime"]=user["bigTime"]=user["workRate"]="out before in"

            else:    # has the right record first in
                now = datetime.datetime.now()
                d2 = datetime.datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                lateastRecord = personLog.order_by('-time')[0].time
                if today==dateStr:  #watch today's workrate
                    bigTime=d2-personLog[0].time   #time now - first in time
                    user['bigtime'] = str(bigTime)
                    stayTime = 0
                    if logNum % 2 == 0:  # if log num is even means he is out now
                        stayTime = personLog[logNum - 1].time - personLog[logNum - 2].time
                        flag = logNum - 3
                    else:  # if it's odd means he is in now
                        stayTime = d2 - personLog[logNum - 1].time
                        flag = logNum - 2
                    while flag > 0:
                        stayTime += personLog[flag].time - personLog[flag - 1].time
                        flag -= 2
                    user["stayTime"] = str(stayTime)
                    user['workRate'] = stayTime / bigTime
                    allRate += stayTime / bigTime

                else:  # watch day before
                    bigTime=lateastRecord-personLog[0].time
                    print(bigTime,lateastRecord,personLog[0].time,"time")
                    user['bigtime'] = str(bigTime)
                    stayTime = 0
                    if logNum % 2 == 0:  # if log num is even means he is out now
                        stayTime = personLog[logNum - 1].time - personLog[logNum - 2].time
                        flag = logNum - 3
                        while flag > 0:
                            stayTime += personLog[flag].time - personLog[flag - 1].time
                            flag -= 2
                        user["stayTime"] = str(stayTime)
                        user['workRate'] = stayTime / bigTime
                        allRate += stayTime / bigTime
                    else:   # if log num is odd, it's ilegal
                        user["stayTime"]=user["bigTime"]=user["workRate"]="has no get off work infor"

            table.append(user)

        averageRate = allRate/len(msgS)
        global  avgRate
        avgRate = averageRate
        #rt_dic['avgRate'] =  averageRate
        res_data['table'] = table
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        rt_dic["result"] = res_data
        return HttpResponse(json.dumps(rt_dic, ensure_ascii=False), content_type="application/json,charset=utf-8")

    def avg(self,requests):
        global avgRate

        dateStr = requests.GET['date']
        today = datetime.datetime.now(timezone).strftime('%Y/%m/%d')
        datedate=dateStr.split('/')
        mth = datedate[1]
        day = datedate[2]
        print(day,mth,"day ,mth")

        table = []
        allRate=0
        today_list = gatelog_table.objects.filter(time__day=day, time__month=mth)
        # msgS = today_list.values_list('workerName').annotate(Count('id'),)
        # print(msgS)
        # count=1
        # for i in msgS:   #give every person's history to web
        #
        #     print(i[0],i[1])
        #     logNum=i[1]
        #     #personLog = today_list.filter(workerName=i[0])
        #     personLog = gatelog_table.objects.filter(time__day=day, time__month=mth,workerName=i[0])
        #     for j in personLog:
        #         print(j.workerName,j.workerId,j.time,j.action)
        #
        #     user = {}
        #     user["key"] = count
        #     count += 1
        #     user["name"] = i[0]
        #     user["id"]=personLog[0].workerId
        #     if personLog[0].action=="out":
        #         user["stayTime"]=user["bigTime"]=user["workRate"]="out before in"
        #
        #     else:    # has the right record first in
        #         now = datetime.datetime.now()
        #         d2 = datetime.datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        #         lateastRecord = personLog.order_by('-time')[0].time
        #         if today==dateStr:  #watch today's workrate
        #             bigTime=d2-personLog[0].time   #time now - first in time
        #             user['bigtime'] = str(bigTime)
        #             stayTime = 0
        #             if logNum % 2 == 0:  # if log num is even means he is out now
        #                 stayTime = personLog[logNum - 1].time - personLog[logNum - 2].time
        #                 flag = logNum - 3
        #             else:  # if it's odd means he is in now
        #                 stayTime = d2 - personLog[logNum - 1].time
        #                 flag = logNum - 2
        #             while flag > 0:
        #                 stayTime += personLog[flag].time - personLog[flag - 1].time
        #                 flag -= 2
        #             user["stayTime"] = str(stayTime)
        #             user['workRate'] = stayTime / bigTime
        #             allRate += stayTime / bigTime
        #
        #         else:  # watch day before
        #             bigTime=lateastRecord-personLog[0].time
        #             print(bigTime,lateastRecord,personLog[0].time,"time")
        #             user['bigtime'] = str(bigTime)
        #             stayTime = 0
        #             if logNum % 2 == 0:  # if log num is even means he is out now
        #                 stayTime = personLog[logNum - 1].time - personLog[logNum - 2].time
        #                 flag = logNum - 3
        #                 while flag > 0:
        #                     stayTime += personLog[flag].time - personLog[flag - 1].time
        #                     flag -= 2
        #                 user["stayTime"] = str(stayTime)
        #                 user['workRate'] = stayTime / bigTime
        #                 allRate += stayTime / bigTime
        #             else:   # if log num is odd, it's ilegal
        #                 user["stayTime"]=user["bigTime"]=user["workRate"]="has no get off work infor"
        #
        #     table.append(user)
        #
        # averageRate = allRate/len(msgS)
        table,avgRate = self.ratePross(today,today_list,dateStr)

        avgRate = avgRate
        rt_dic = {}
        res_data = {}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        rt_dic["result"]=res_data

        res_data["avgRate"]= avgRate
        res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        return HttpResponse(json.dumps(rt_dic, ensure_ascii=False), content_type="application/json,charset=utf-8")


    def weekPeople(self,requests):
        rt_dic = {}
        res_data = {}
        counter={}
        rt_dic['code'] = 0
        rt_dic['message'] = "REQUEST_SUCCESS"
        today=datetime.date.today()
        monday, sunday = today,today
        one_day = datetime.timedelta(days=1)
        fToday = datetime.date.today()+ one_day
        while monday.weekday() != 0:
            monday -= one_day
        # while sunday.weekday() != 6:
        #     sunday += one_day
        record_day = monday
        weeknum=0
        while record_day != fToday:
            recordDay_list = gatelog_table.objects.filter(time__range=(record_day, record_day+one_day))  # people today
            msgToday = recordDay_list.values_list('workerName').annotate(Count('id'))
            weeknum+=len(msgToday)
            record_day=record_day+one_day

        today_list = gatelog_table.objects.filter(time__range=(today,fToday)) #people today
        msgToday = today_list.values_list('workerName').annotate(Count('id'))
        counter["week"]=weeknum
        counter['up']=len(msgToday)
        global workersInRegion
        WorkersNum = 0
        for num in workersInRegion:
            WorkersNum += num
        counter['now'] = WorkersNum
        res_data["counter"]=counter
        rt_dic["result"]=res_data
        return HttpResponse(json.dumps(rt_dic, ensure_ascii=False), content_type="application/json,charset=utf-8")



# def index(request):   # the parameter is requese (which include get/post, broswe system info )
#     return HttpResponse(u"o my gash")    #return to web
# # Create your views here.
#
# def add(request):
#     a = request.GET['a']    # get the
#     b = request.GET['b']
#     c = int(a)+int(b)
#     return HttpResponse(str(c))
#
#
# def add2(request, a, b):
#     c = int(a) + int(b)
#     return HttpResponse(str(c))
#
#
#
# def dict(request):
#     rt_dic = {}
#     res_data = {}
#     rt_dic['code'] = 0
#     rt_dic['message'] = "REQUEST_SUCCESS"
#     users = '我'
#     # workersThroughGate.clear()
#     res_data['users'] = users
#     res_data['timestamp'] = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
#     rt_dic['result'] = res_data
#     return HttpResponse(json.dumps(rt_dic,ensure_ascii=False),content_type="application/json,charset=utf-8")


