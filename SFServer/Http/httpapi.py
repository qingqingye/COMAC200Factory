#coding=utf-8
from flask import Flask,request,jsonify
from flask_cors import CORS
from apitest import testapi


app = Flask(__name__,static_folder='./static')
CORS(app, resources={r'/*': {"origins": "*"}})


@app.route('/factory/getWorkerList/', methods=['GET'])
def getWorkerList():
    #try:
    fid =  request.args.get('fID')
    print(fid)
    if(fid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getworkerlist(fid))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})



@app.route('/factory/getWorkersThroughEntry/', methods=['GET'])
def getWorkersThroughEntry():
    #try:
    fid =  request.args.get('fid')
    print(fid)
    if(fid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getworkersthroughentry(fid))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/factory/count', methods=['GET'])
def getCounter():
    #fid =  request.args.get('fID')
    #print(fid)
    #if(fid is None):
    #    return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getWorkerCount(0))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/factory/statistic', methods=['GET'])
def getStatistic():
    #fid =  request.args.get('fID')
    #print(fid)
    #if(fid is None):
    #    return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getWorkerStatistic(0))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/gate', methods=['GET'])
def getGate():
    #gid =  request.args.get('fID')
    #print(gid)
    #if(gid is None):
    #    return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getGateInfo())
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/flv', methods=['GET'])
def getFlv():
    cid =  request.args.get('camid')
    print(cid)
    if(cid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getFlvUrl(cid))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})

@app.route('/trajectory', methods=['GET'])
def trace():
    fid =  request.args.get('fID')
    fid = int(request.args['fid'])
    print(fid,'fID')
    if(fid is None):
       return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getTrace(fid))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})


@app.route('/getInfo',methods=['GET'])
def getInfo():
    fid = request.args.get('fID')
    fid = int (request.args['fid'])
    print (fid , 'fid')
    if ( fid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getInformation(fid))    
    

@app.route('/factory/getWorkerLocation/', methods=['GET'])
def getWorkerLocation():
    #try:
    fid =  request.args.get('fID')
    fid = int(request.args['fid'])
    print(fid,'fid')
    if(fid is None):
        return jsonify({'op_code': -1, 'op_msg': 'FID Not Found', 'source': 'DataServer'})
    return jsonify(testapi.getworkerlocation(fid))
    #except exception_base.APIProviderException as e:
    #    return jsonify({'op_code': e.errcode, 'op_msg': str(e), 'source': 'DataServer'})