
# coding: utf-8

# In[1]:
import math
import datetime
import sqlite3 as sql
from prettytable import from_db_cursor
import json
import base64
import datetime

# area: -10 means not in the work area ; 1 means at workarea1 

################## a function to check the table  ################
def pt_table(conn,tablename):
    cur=conn.cursor()
    sql='SELECT * FROM '+ tablename
    cur.execute(sql)
    pt = from_db_cursor(cur)
    print(pt)
    
    
def frame_area(frame):
    return(math.pow(frame[0]-frame[2] , 2) + math.pow(frame[1]-frame[3] ,2 ))
    
    
def create(conn):
     # `id`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,

    sql_heatmap='CREATE TABLE IF NOT EXISTS ' + ' heatmap_table' + '''( 
      A INT,
      B INT,
      C INT,
      D INT,
      E INT,
      F INT,
      G INT,
      H INT,
      date timestamp not null default (datetime('now','localtime'))
    )'''
    # 用 execute 执行一条 sql 语句
    conn.execute(sql_heatmap)

    sql_gate = 'CREATE TABLE IF NOT EXISTS ' + ' gate_table' + '''(
      id INT,  
      name TEXT,
      action TEXT,
      date timestamp not null default (datetime('now','localtime'))
    )'''
    conn.execute(sql_gate)

    print('build table successfully')

def get_date_db():
    
    today=datetime.date.today()
    formatted_today=today.strftime('%y%m%d')
  #  db_path=formatted_today+'.db'
    return (formatted_today)
 


def select(conn, num ,table):
    """
    根据员工的工号查询数据
    """
    
    sql_sbynum='''SELECT * ,Max(date) FROM ''' + table + ''' WHERE  id=%d'''
    cursor = conn.execute(sql_sbynum %num)
    return list(cursor)
    
    
def insert_heat(conn,A,B,C,D,E,F,G,H):
    sql_insert='INSERT INTO ' + 'heatmap_table' +'''( A,B,C,D,E,F,G,H )
    VALUES
      (?,?, ?, ?,?,?,?,?);
    '''
    conn.execute(sql_insert,(A,B,C,D,E,F,G,H))
    print('HEATMAP PUT ')


def insert_gate(conn,id,name,action):
    sql_insert='INSERT INTO '+'gate_table' +'''(id , name , action  )
    VALUES
      (?,?,?);
    '''
    conn.execute(sql_insert, (id, name, action))
    print('GATE PUT')

    
# if the worker has change the area 
def update_area(conn,user_id,area_now,mj , zero ,last ): # zero is something to tell me whether i need to add 0 or -1
    trace_select = 'SELECT trace,area_now,stay_time FROM table_workertoday WHERE user_id =%d'   # 0:trace  1:areanow 2staytime
    trace_info = conn.execute(trace_select%user_id).fetchone()
#     trace = trace_info[0] + str(trace_info[1]) + ":" + str(trace_info[2]+ zero) +','
    timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    trace = trace_info[0] + str(trace_info[1]) + "_" + timenow + "," + str(area_now) + "_" + timenow + ","
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




def traceBack(trace):
    out=trace.split(',')
    backTrace=''
    for i in out[0:-2] :
        backTrace += i + ',' 
    back=out[-2].split(':')
#    back[0]:back area    back[1]:back time
    return ( int(back[0]) ,int( back[1]) , backTrace)

    
def create_allworker(allworker_data, database ):   # if there isn't any new worker ,don't run it
#################### make a table contains all workers in this factory #####################
    import sqlite3 as sql
    db_path=get_date_db()
    conn = sql.connect(database)
    print("打开了数据库")
    try:
        conn.execute('DROP TABLE table_workerall')    # drop the table before to avoid database dropping
    except:
        pass
    
    sql_create='''CREATE TABLE IF NOT EXISTS table_workerall ( 
    user_id  INT NOT NULL UNIQUE,
    user_name  TEXT,
    post TEXT,
    pic TEXT,
    authority TEXT 
    
    )'''
    # 用 execute 执行一条 sql 语句
    conn.execute(sql_create)
    
    pt_table(conn,'table_workerall')
    for i in allworker_data:
        try:    
            picid=str(i[0])+ '.jpg'
            with open("C:\\Users\\24330\\Desktop\\yoke\\COMAC200Factory-master\\picture\\" + picid , 'rb') as f:
                base64_data = base64.b64encode(f.read())
                s = base64_data.decode()
        except:
            s = ''
        conn.execute('''INSERT INTO table_workerall (user_id,user_name,'post','authority','pic')VALUES (?,?,?,?,?);'''
                     , (i[0],i[1],i[2],i[3],s))
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
    conn.commit()
    pt_table(conn,'table_workertoday')
    conn.close()
    
    
    
    