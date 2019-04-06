#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append('./AutoID_ML')

from flask import Flask, request
from flask_cors import *
import queue
import json
import threading
import DatabaseHandler as db
from detection import detection
import util
from argparse import ArgumentParser
import soco
import yeelight

app = Flask(__name__)
CORS(app, supports_credentials=True)
config = util.loadConfig()
dt = detection()
save_mode = False
sensingdict = dict()

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
    if util.DEBUG:
        print(objList)
    return json.dumps(j)

@app.route('/all-objects-state', methods=['GET'])
def get_all_state():
    global sensingdict
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
    sensingdict = dt.getSensingresult()
    semList = []
    l = len(epcList)
    for key in sensingdict.keys():
        sem = db.mongoHandler.getTagSemantic(key, sensingdict[key])
        semList.append(sem)
    # for i in range(0, l):
    #     if i >= len(infoList) or infoList[i] == '':
    #         semList.append('undetected')
    #     else:
    #         sem = db.mongoHandler.getTagSemantic(epcList[i], infoList[i])
    #         semList.append(sem)
    # if util.DEBUG:
    #     print(str(infoList)+str(objList) + str(semList))
    for o in objList:
        state[o] = semList[leftIndex[o]:rightIndex[o]]
    # if save_mode:
    #     db.mongoHandler.saveRecognized(state)
    return json.dumps(state)


@app.route('/get-toggle', methods=['GET'])
def get_toggles():
    toggleList = db.mongoHandler.getToggles()
    j = {'toggle': toggleList}
    return json.dumps(j) 

@app.route('/remove-object', methods=['POST'])
def remove_object():
    objName = request.form['objName']
    db.mongoHandler.removeObject(objName)
    return 'success'


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

def control_init():
    # bulb and sonos init
    sonos = soco.SoCo('192.168.3.159')
    # bulb = yeelight.Bulb(yeelight.discover_bulbs(timeout=10)[0].get('ip'))
    bulb = yeelight.Bulb('192.168.3.155')

    print(sonos)
    if sonos:
        sonos.play_mode = 'REPEAT_ONE'
        sonos.play_uri('http://img.tukuppt.com/newpreview_music/09/01/52/5c89f044e48f61497.mp3')
        sonos.volumn = 6
        sonos.mute = False
    print(bulb)
    if bulb:
        bulb.turn_off()
        # bulb.set_brightness(10)

    return sonos, bulb


def control_task(sonos, bulb, r_event, eventlist):
    global sensingdict
    # phone status
    muteFlag = False
    phoneEPC = 'E20000193907010113104906'
    EPClist = ['E2000019390700211300052E']
    iiii = 0

    print("start!!!!")
    while r_event.is_set():
        # print('control', sensingdict)
        if phoneEPC in sensingdict.keys():
            phonestatus = sensingdict[phoneEPC]
        else:
            phonestatus = False
        # press event
        dt.updateInteractionEPC(EPClist)
        for event in eventlist:
            if event.is_set():
                if phonestatus:
                    print("sonos.mute:", sonos.mute)
                    muteFlag = ~muteFlag
                    sonos.mute = muteFlag
                else:
                    print("bulb lighted")
                    bulb.toggle()
                    bulb.set_brightness(10)
                print("true", iiii)
                event.clear()
                iiii += 1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-s", "--save", action="store_true", help="Do you want to save the raw data to the mongodb or not?")
    args = parser.parse_args()

    r_event = threading.Event()
    r_event.set()
    up_event = threading.Event()
    eventlist = [up_event]
    sonos, bulb = control_init()
    if args.save:
        save_mode = True
        rawDBHandler = db.DatabaseHandler()
        t1 = threading.Thread(target=dt.detect_status, args=(config['readerIP'], config['readerPort'],r_event,eventlist,rawDBHandler))
    else:
        save_mode = False
        t1 = threading.Thread(target=dt.detect_status, args=(config['readerIP'], config['readerPort'],r_event,eventlist,))

    resetThread = threading.Thread(target=dt.resetEPC, args=())
    t2 = threading.Thread(target=control_task, args=(sonos,bulb,r_event, eventlist,))
    t1.start()
    t2.start()
    resetThread.start()
    app.run(port=8888, debug=False, host='0.0.0.0')

