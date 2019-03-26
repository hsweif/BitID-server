import sys
sys.path.append('./AutoID_ML')

from flask import Flask, request
from flask_cors import *
import DataHandler
import queue
import json
import threading
import DatabaseHandler as db
from DataHandler import DataHandler
import fromback as fb
import util

vueUpdateEPCUrl = 'http://localhost:8000/updateEPC'
interval = 3

app = Flask(__name__)
CORS(app, supports_credentials=True)
q = queue.Queue()
stop = threading.Event()
dataHandler = DataHandler(stop)
config = util.loadConfig()
#fb.receivedata(config['readerIP'], config['readerPort'])

@app.route('/')
def hello_world():
    return 'hello world'

@app.route('/save-tag', methods=['POST'])
def save_tag():
    content = request.form['content']
    print(content)
    db.mongoHandler.insertTag(json.loads(content))
    return 'success'

@app.route('/update-epc', methods=['GET'])
def update_EPC():
    if util.DEBUG:
        epc = dataHandler.getTopTag()
        print(epc)
    return dataHandler.getTopTag()

@app.route('/get-complex-objects', methods=['GET'])
def get_complex_objects():
    raw_objList = db.mongoHandler.getObjects()
    objList = []
    cnt = 0
    for raw in raw_objList:
        objList.append({"label_value": cnt, "label_name": raw})
        cnt = cnt + 1
    j = {'objects': objList}
    return json.dumps(j) 

@app.route('/get-objects', methods=['GET'])
def get_objects():
    objList = db.mongoHandler.getObjects()
    j = {'objects': objList}
    return json.dumps(j)

@app.route('/get-object-state', methods=['POST'])
def get_object_state():
    objName = request.form['objName']
    epcList = db.mongoHandler.getRelatedTag(objName, 'Sensor')
    print(objName)
    infoList = fb.processdata(epcList)
    state_list = []
    cnt = 0
    if util.DEBUG:
        infoList = [True]
    for item in infoList:
        sem = db.mongoHandler.getTagSemantic(epcList[cnt], item)
        print(sem)
        state_list.append(sem)
        cnt = cnt + 1
    j = {'info': state_list}
    return json.dumps(j) 

if __name__ == '__main__':
    dataHandler.start()
    app.run(port=8888, debug=True)
