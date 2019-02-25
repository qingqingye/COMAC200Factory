
# coding: utf-8

# In[1]:


import numpy as np
import datetime
import sqlite3 as sql
from prettytable import from_db_cursor
import data

# area: -10 means not in the work area ; 1 means at workarea1 

################## a function to check the table  ################
def pt_table(conn,tablename):
    cur=conn.cursor()
    sql='SELECT * FROM '+ tablename
    cur.execute(sql)
    pt = from_db_cursor(cur)
    print(pt)
    
    
def frame_area(frame):
    return(np.square(frame[0]-frame[2])+np.square(frame[1]-frame[3]))
    
    
def create(conn, area_string):
    """
    创建相应的数据表
    """
     # `id`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,

    sql_create='CREATE TABLE IF NOT EXISTS '+area_string+'''(  
      user_id  INT NOT NULL UNIQUE,
      user_name  TEXT ,
      area_now INT,
      stay_time  INT NOT NULL,
      frame_area INT,
      trace TEXT,
      plan_trace TEXT,
      has_update INT,
      workpiece TEXT
    )'''
    
    # 用 execute 执行一条 sql 语句
    conn.execute(sql_create)
    
    print('创建成功:',area_string)

    

def get_date_db():
    
    today=datetime.date.today()
    formatted_today=today.strftime('%y%m%d')
  #  db_path=formatted_today+'.db'
    return (formatted_today)
 

def  initialize(conn,worker_data):
    for i in worker_data:
        hello_worker='number:'+str(i[0])+'  name:'+i[1]+"  today's plan is  "
        plan_trace='plan'
        #plan_trace= input(hello_worker)
        insert(conn,'table_workertoday',i[0], i[1], -10 ,0,0,'',plan_trace,0) 
        # area_string
        # user_id | user_name | area_now | stay_time | frame_area | trace | plan_trace | has_update | 
    

def select_bynum(conn,area_string, num ):
    """
    根据员工的工号查询数据
    """
    
    sql_sbynum='''SELECT *  FROM ''' +  area_string + ''' WHERE   user_id=?'''
    cursor = conn.execute(sql_sbynum, num)
    #return list(cursor)
    print('一条数据',list( cursor))
    
    
def insert(conn,area_string,user_id, user_name, area_now,stay_time,frame_area,trace,plan_trace,has_update):
    """
    插入一行的数据
    
    """

    sql_insert='INSERT INTO '+area_string+'''(user_id,user_name,area_now, stay_time , 
    frame_area,trace,plan_trace,has_update)
    VALUES
      (?,?,?, ?, ?,?,?,?);
    '''
    conn.execute(sql_insert, (user_id, user_name, area_now,stay_time,frame_area,trace,plan_trace,has_update))   
    print('插入数据成功')

    
# if the worker has change the area 
def update_area(conn,user_id,area_now,mj , zero ,last ): # zero is something to tell me whether i need to add 0 or -1
    trace_select = 'SELECT trace,area_now,stay_time FROM table_workertoday WHERE user_id =%d'
    trace_info = conn.execute(trace_select%user_id).fetchone()
    trace = trace_info[0] + str(trace_info[1]) + ":" + str(trace_info[2]+ zero) +','
    a = "UPDATE \'table_workertoday\' \n" +     "SET stay_time=1, area_now ={} ,trace=\'{}\', frame_area={}, has_update={}\n".format(area_now, trace, mj , trace_info[1]) +     "WHERE user_id={}".format(user_id)
    # area_now | stay_time | frame_area | trace | has_update
    conn.execute(a) 

    

def update_staytime(conn, user_id ,mj ):
#     time = conn.excute('''SELECT stay_time FROM workers  ''')
    """
    更新相应部分的数据
    """
    
    sql_update='''UPDATE  table_workertoday  SET
      stay_time = table_workertoday.stay_time+1 ,has_update=-1 , frame_area=%d  WHERE   user_id=%d
    '''
    conn.execute(sql_update%(mj,user_id))


def for_vedio(conn,area_list,toSecond):
    for time in range (0,toSecond):      #every frame , need renew tables  
        conn.execute ('UPDATE table_workertoday  SET has_update=0')
        for i in area_list:     # i[0]is array ; i[1] is table name
        #in this time  this area  contains whom 
            for person in i[0][time]:     #person[x,y,x,y,id]
                if person!=[]:
                    mj=int(frame_area(person[:4]))
                    update(conn,person[4] , i[1] ,mj)
        ####  if the worker is not in any area this time we think he is out ##########
        sql= 'SELECT  area_now, user_id  FROM table_workertoday WHERE has_update=0'
        last_area=conn.execute(sql).fetchall()   #lastarea[0]:area name  lastarea[1]:user_id
        for i in last_area :
            if i[0]==-10:  # -10  means outdoor 
                update_staytime(conn,i[1],0)   # user_id ,mj
            else : 
                update_area(conn,i[1], -10 , 0 ,0 ,i[0])  #user_id , area_now, mj , zero ,last 
        pt_table(conn,'table_workertoday')
        print('herereeeeeeeeeeeeeeeeeeeeeeeeeeee',time)

def traceBack(trace):
    out=trace.split(',')
    backTrace=''
    for i in out[0:-2] :
        backTrace += i + ',' 
    back=out[-2].split(':')
#    back[0]:back area    back[1]:back time
    return ( int(back[0]) ,int( back[1]) , backTrace)

    
                
def duplicateRemoval(conn,user_id , mj ,area_now): #old[0] mj   old[1] update old[2] trace
    pt_table(conn,'table_workertoday')
    old = conn.execute('SELECT frame_area, has_update , trace FROM table_workertoday WHERE user_id=%d' %user_id).fetchone()
    dValue = mj - old[0]
    print(dValue , 'dddd')
    ## last time I do update_time
    if old[1] == -1: 
        print('last time do update time ')
        if dValue > 3000 :
            update_area(conn , user_id , mj , -1)
    ## last time I do update_area
    else:   
        print('last time do update area')
        print(old[2],'trace')
        if area_now == old[1] :   # I will do update_time     
            print('now i do time')
            if dValue >= -3000:
                backa,backt, Ntrace = traceBack( old[2] ) 
                sql='''UPDATE table_workertoday SET area_now= {}, stay_time = {}, trace=\' {} \' WHERE user_id = {}'''.format(backa,backt,Ntrace,user_id)
                conn.execute(sql)
                update_staytime(conn, user_id ,mj)
            else: pass
         
        else: # I will do update_area  
            print('now  i do area' )
            if dValue >= 0:
                a = "UPDATE \'table_workertoday\' \n" + "SET  area_now ={} , frame_area={} ".format(area_now, mj )                 + "WHERE user_id={}".format(user_id)
                 # area_now | stay_time | frame_area | trace | has_update
                conn.execute(a)
            else: pass
            

        
def update(conn,user_id , area_now ,mj) :#(conn,area_string,user_id, user_name, area_now,stay_time,frame_area,trace,plan_trace,has_update):
    
    sql_last = '''SELECT area_now , has_update FROM 'table_workertoday' WHERE user_id=%d'''
    last_area = conn.execute(sql_last%user_id).fetchone()   
    #last_area[0]:area num  last_area[1]: whether it has been update. If YES need depulicte move function

    ######   if last_area !=none means the num is in the worker list, he is a worker   #################

    if last_area != None:
        if last_area[1] !=0  :
            # this worker  has been updated 
            print(' duplicate')
            duplicateRemoval(conn , user_id ,mj ,area_now )
            
        else:  # this worker doesn't need duplicateremove
            if last_area[0] == area_now: # still in last area 
                update_staytime(conn, user_id ,mj )
            else:  #appear in a new area 
                update_area(conn,user_id, area_now, mj , 0 , last_area[0])
                # user_id,area_now,mj , zero ,last 
    ######### a visitor is anyone who is not in the worker table #####################        
    else:
        print('he is a visitor ')

        

def initial_10tables(path_name,area_list):
    date=get_date_db()
    db_path=  date+'.db'
    conn = sql.connect(path_name)
    print("打开了数据库")

    conn_fixed = sql.connect('guding.db')
    ############################# create 10 tables###################################

    ############################## table_vistor ################################
    sql_create='''CREATE TABLE IF NOT EXISTS table_visitortoday ( visitor  TXT , area_now  TEXT )'''
    conn.execute(sql_create)
    pt_table(conn,'table_visitortoday')
    ########  table_workertoday  +  table_areax #########################

    create(conn,'table_workertoday')
    for i in area_list:
        create(conn,'a' + str(i[1]))

    #############################  initialize big table  ########################################    
    initialize(conn,data.worker_data)
     #user_id user_name  area_now stay_time frame_area trace  plan_trace  has_update 
    pt_table(conn,'table_workertoday')   
    ############################ update the big table now  ######################################

    conn.commit()
    conn.close()
    return (db_path) #return the database we use today
  
    
def create_allworker(allworker_data):   # if there isn't any new worker ,don't run it
#################### make a table contains all workers in this factory #####################
    import sqlite3 as sql
    db_path=get_date_db()
    conn = sql.connect('guding.db')
    print("打开了数据库")
    conn.execute('DROP TABLE table_workerall')    # drop the table before to avoid database dropping
    sql_create='''CREATE TABLE IF NOT EXISTS table_workerall ( 
    user_id  INT NOT NULL UNIQUE,
    user_name  TEXT,
    post TEXT,
    authority TEXT)'''
    # 用 execute 执行一条 sql 语句
    conn.execute(sql_create)

    for i in allworker_data:
   
        conn.execute('''INSERT INTO table_workerall (user_id,user_name,'post','authority')VALUES (?,?,?,?);'''
                     , (i[0],i[1],i[2],i[3]))
        print('插入数据成功')
    pt_table(conn,'table_Workerall')
    conn.commit()
    conn.close()
    print('close 数据库')
    
    
def change_allworker(allworker_data):
    return 0
    
    


def workpiece(conn,piece_name,user_id):
    a = "UPDATE \'table_workertoday\' \n" +  "SET workpiece=\'{}\' \n".format(piece_name) +  "WHERE user_id={}".format(user_id)
    conn.execute(a) 
    pt_table(conn,'table_workertoday')