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
from detection import detection
import util

vueUpdateEPCUrl = 'http://localhost:8000/updateEPC'
interval = 3

app = Flask(__name__)
CORS(app, supports_credentials=True)
config = util.loadConfig()
dt = detection()

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
        # epc = dataHandler.getTopTag()
        epc = dt.getTopTag()
        print(epc)
    return dt.getTopTag()

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
    print(objList)
    return json.dumps(j)

@app.route('/get-toggle', methods=['GET'])
def get_toggles():
    # TODO: implement toggle return
    toggleList = db.mongoHandler.getToggles()
    j = {'toggle': toggleList}
    return json.dumps(j) 


@app.route('/get-toggle-action', methods=['POST'])
def get_toggle_action():
    togName = request.form['toggle']
    toggleAction = []
    rawAction = db.mongoHandler.getToggleControl(togName)
    cnt = 0
    for raw in rawAction:
        toggleAction.append({"label_value": cnt, "label_name": raw})
        cnt = cnt + 1
    j = {'action': toggleAction}
    return json.dumps(j)

@app.route('/get-object-sem', methods=['POST'])
def get_object_sem():
    objName = request.form['objName']
    semList = []
    rawList = db.mongoHandler.getSensorSemantic(objName)
    if util.DEBUG:
        print(objName)
        print(rawList)
    cnt = 0
    for raw in rawList:
        semList.append({"label_value": cnt, "label_name": raw})
        cnt = cnt + 1
    j = {'semantic': semList}
    return json.dumps(j)

@app.route('/get-object-state', methods=['POST'])
def get_object_state():
    objName = request.form['objName']
    epcList = db.mongoHandler.getRelatedTag(objName, 'Sensor')
    dt.updateSensingEPC(epcList)
    infoList = dt.getSensingresult() 
    if util.DEBUG:
        print(epcList)
        print(infoList)
    state_list = []
    cnt = 0
    for item in infoList:
        sem = db.mongoHandler.getTagSemantic(epcList[cnt], item)
        if util.DEBUG:
            print(sem)
        state_list.append(sem)
        cnt = cnt + 1
    j = {'info': state_list}
    return json.dumps(j) 

if __name__ == '__main__':
    recvThread = threading.Thread(target=dt.receivedata, args=(config['readerIP'], config['readerPort']))
    prThread = threading.Thread(target=dt.processdata, args=())
    resetThread = threading.Thread(target=dt.resetEPC, args=())
    recvThread.start()
    prThread.start()
    resetThread.start()
    app.run(port=8888, debug=True)
