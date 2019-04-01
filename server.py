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
from argparse import ArgumentParser

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
    db.mongoHandler.insertTag(json.loads(content))
    return 'success'

@app.route('/update-epc', methods=['GET'])
def update_EPC():
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

@app.route('/all-objects-state', methods=['GET'])
def get_all_state():
    state = {}
    objList = db.mongoHandler.getObjects()
    leftIndex = {}
    rightIndex = {}
    epcList = []
    index = 0
    for o in objList:
        leftIndex[o] = index
        epclist = db.mongoHandler.getRelatedTag(o, 'Sensor')
        for e in epclist:
            index += 1
            epcList.append(e)
        rightIndex[o] = index
    dt.updateSensingEPC(epcList)
    infoList = dt.getSensingresult() 
    semList = []
    l = len(epcList)
    for i in range(0, l):
        if i >= len(infoList) or infoList[i] == '':
            semList.append('undetected')
        else:
            sem = db.mongoHandler.getTagSemantic(epcList[i], infoList[i])
            semList.append(sem)
    for o in objList:
        state[o] = semList[leftIndex[o]:rightIndex[o]]
    print(state)
    return json.dumps(state)


@app.route('/get-toggle', methods=['GET'])
def get_toggles():
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
    state_list = []
    cnt = 0
    for item in infoList:
        if cnt >= len(epcList):
            break
        sem = db.mongoHandler.getTagSemantic(epcList[cnt], item)
        state_list.append(sem)
        cnt = cnt + 1
    j = {'info': state_list}
    return json.dumps(j) 

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-s", "--save", action="store_true", help="Do you want to save the raw data to the mongodb or not?")
    args = parser.parse_args()

    r_event = threading.Event()
    r_event.set()
    up_event = threading.Event()
    eventlist = []
    if args.save:
        rawDBHandler = db.DatabaseHandler()
        t1 = threading.Thread(target=dt.detect_status, args=(config['readerIP'], config['readerPort'],r_event,eventlist,rawDBHandler))
    else:
        t1 = threading.Thread(target=dt.detect_status, args=(config['readerIP'], config['readerPort'],r_event,eventlist))
    resetThread = threading.Thread(target=dt.resetEPC, args=())
    t1.start()
    resetThread.start()
    app.run(port=8888, debug=True)
