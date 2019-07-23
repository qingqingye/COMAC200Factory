from Http import httpapi
from database import mylib
import sqlite3 as sql
""" testapi.loadImageNames()
testapi.loadHeatmapData()
testapi.runCounter() """
#testapi.loadHeatmapData()
#testapi.runCounter()

path='C:\\Users\\24330\\Desktop\\Server-Nvr\\database\\info.db'
conn = sql.connect(path)
mylib.create(conn)
conn.close()
httpapi.app.run(host='0.0.0.0', port=8008, threaded=True, debug=False)
