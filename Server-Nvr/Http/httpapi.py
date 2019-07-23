from flask import Flask,request,jsonify
from flask_cors import CORS
from DataProcessor.dataProcessor import *

app = Flask(__name__,static_folder='./static')
CORS(app, resources={r'/*': {"origins": "*"}})

dataCenter = DataProcessor()

@app.route('/factory/getWorkerList/', methods=['GET'])
def getWorkerList():
    #try:

    return jsonify({'op_code': -2, 'op_msg': 'Api Duplicated', 'source': 'SFDataServer'})

    """ fid =  request.args.get('fID')
    print(fid)
    if(fid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getworkerlist(fid)) """
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/factory/getWorkerLocation/', methods=['GET'])
def getWorkerLocation():
    #try:

    return jsonify({'op_code': -2, 'op_msg': 'Api Duplicated', 'source': 'SFDataServer'})

    """ fid =  request.args.get('fID')
    print(fid)
    if(fid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getworkerlocation(fid)) """
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/factory/getWorkersThroughEntry/', methods=['GET'])
def getWorkersThroughEntry():
    #try:

    return jsonify({'op_code': -2, 'op_msg': 'Api Duplicated', 'source': 'SFDataServer'})

    """ fid =  request.args.get('fID')
    print(fid)
    if(fid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getworkersthroughentry(fid)) """
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/factory/count', methods=['GET'])
def getCounter():
    #fid =  request.args.get('fID')
    #print(fid)
    #if(fid is None):
    #    return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    #return jsonify(testapi.getWorkerCount(0))
    return jsonify(dataCenter.getWorkerCount(0))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/factory/statistic', methods=['GET'])
def getStatistic():
    #fid =  request.args.get('fID')
    #print(fid)
    #if(fid is None):
    #    return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    #return jsonify(testapi.getWorkerStatistic(0))
    return jsonify(dataCenter.getWorkerStatistic(0))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/gate', methods=['GET'])
def getGate():
    #gid =  request.args.get('fID')
    #print(gid)
    #if(gid is None):
    #    return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    #return jsonify(testapi.getGateInfo())
    return jsonify(dataCenter.getGateInfoAsync())
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/flv', methods=['GET'])
def getFlv():
    return jsonify({'op_code': -2, 'op_msg': 'Api Duplicated', 'source': 'SFDataServer'})
    """ cid =  request.args.get('camid')
    print(cid)
    if(cid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getFlvUrl(cid)) """
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/heatmap', methods=['GET'])
def getHeatmap():
    #fid =  request.args.get('fID')
    #print(fid)
    #if(fid is None):
    #    return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    #return jsonify(testapi.getHeatmap())
    return jsonify(dataCenter.getHeatmap())
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})



