#coding=utf-8

import time
import random
import sqlite3 as sql
import re

def randomLocation(list, t):
    x0 = list[0]
    x1 = list[1]
    y0 = list[2]
    y1 = list[3]

    tempdict={}
    tempdict['x'] = random.uniform(x0, x1)
    tempdict['y'] = random.uniform(y0, y1)
    tempdict['time'] = t
    return tempdict

def helpTrace(fid):
    conn = sql.connect('C:\\Users\\24330\\Desktop\\yoke\\SFServer\\apitest\\1.db')
    sql_sbynum='''SELECT trace  FROM  table_workertoday  WHERE  user_id=%d'''
    cursor = conn.execute(sql_sbynum %fid)
    infoList=list(cursor)[0][0]
    a=re.split('[,_]',infoList)
    order=list(map(int,a[:len(a)-1:2]))
    torder=a[1::2]
    return order,torder


def getTrace(fid):
    order,torder = helpTrace(fid)
    print(order,torder)
    areaNew=[]
    #[x0,x1,y0,y1]
    coordinate = [[],[3, 10.2, 4, 6], [4, 6.3, 0, 4], [],
                  [0, 4, 6, 10], [4, 6.3, 6, 10], [0, 4, 0, 4], [0, 4, 4, 6], [6.3, 10, 6, 10], [6.3, 10, 0, 4]]
    #order = [5, 1, 8, 0, 6, 3, 4, 7]
    for i in range (len(order)):
        area=order[i]
        if area ==-10:
            pass
        else:
            tempdict = randomLocation(coordinate[area], torder[area])
            areaNew.append(tempdict)
       

    rt_dic = {}
    res_data = {}
    rt_dic['code'] = 0
    rt_dic['message'] = "success"

    #    heatidx = 0

    res_data['trajectory'] = areaNew
    res_data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    rt_dic['result'] = res_data
    return rt_dic
 
    
def getworkerlocation(fid): 
    conn = sql.connect('C:\\Users\\24330\\Desktop\\yoke\\SFServer\\apitest\\data.db')
    # conn.text_factory=str
    print('connect seccuss')
    sql_sbynum='''SELECT *  FROM  table_workerall  WHERE  user_id=%d'''
    cursor = conn.execute(sql_sbynum %fid)
    info={}
    infoList=list(cursor)[0]
    info['name']= infoList[1]
    info['post'] = infoList[2]
    info['authority']=infoList[3]
    conn.close()
    
    conn = sql.connect('C:\\Users\\24330\\Desktop\\yoke\\SFServer\\apitest\\1.db')
    # conn.text_factory=str
    sql_sbynum='''SELECT *  FROM  table_workertoday  WHERE  user_id=%d'''
    cursor = conn.execute(sql_sbynum %fid)
    infoList=list(cursor)[0]
    location={'area':infoList[2],'t': infoList[3],  'trace':infoList[5] , 'piece':infoList[8] }
    conn.close()
    
    Flist=[]
    Flist.append(info)
    Flist.append(location)
    
    rt_dic = {}
    res_data = {}
    rt_dic['code'] = 0
    rt_dic['message'] = "成功"

    res_data['trajectory'] = Flist
    res_data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    rt_dic['result'] = res_data
    return rt_dic


def getHeatmap():
    #global heatidx
    areas = [
        {
            "x":0,
            "y":0,
            "tmp":0
        },
        {#1
            "g":6,
            "l":2,
            "tmp":299
        },
        {#2
            "g":4.9,
            "l":5.3,
            "tmp":326
        },
        {#3
            "g":4,
            "l":3.65,
            "tmp":262
        },
        {#4
            "g":3.7,
            "l":2,
            "tmp":184
        },
        {#5
            "g":3.7,
            "l":5.3,
            "tmp":123
        },
        {#6
            "g":4.9,
            "l":2,
            "tmp":184
        },
        {#7
            "g":6.2,
            "l":3.65,
            "tmp":312
        },
        {#8
            "g":6,
            "l":5.3,
            "tmp":342
        },
        {
            "g":9,
            "l":8,
            "tmp":0
        }
    ]
    rt_dic = {}
    res_data = {}
    rt_dic['code'] = 0
    rt_dic['message'] = "success"

    #    heatidx = 0
    areas[0]['tmp'] = 0
    areas[9]['tmp'] = 0
    res_data['areas'] = areas
    res_data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    rt_dic['result'] = res_data
    return rt_dic

def getInformation(fid):
    conn = sql.connect('C:\\Users\\24330\\Desktop\\yoke\\SFServer\\apitest\\data.db')
    sql_sbynum='''SELECT user_name , post , authority FROM allworker_data WHERE  user_id=%d'''
    cursor = conn.execute(sql_sbynum %fid)
    conn.close()
        
    rt_dic = {}
    res_data = {}
    rt_dic['code'] = 0
    rt_dic['message'] = "成功"

    res_data['trajectory'] = Flist
    res_data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    rt_dic['result'] = res_data
    return rt_dic
    


def main():
    print(getTrace(10))
    
if __name__ == '__main__':
    main()   