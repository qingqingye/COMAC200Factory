#coding=utf-8
from Http import httpapi
from Http import httpapi
from apitest import testapi

# testapi.loadImageNames()
# testapi.loadHeatmapData()
# testapi.runCounter()

httpapi.app.run(host='0.0.0.0', port=8008, threaded=True, debug=True)