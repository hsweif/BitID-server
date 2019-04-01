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
import soco
import yeelight

vueUpdateEPCUrl = 'http://localhost:8000/updateEPC'
interval = 3

app = Flask(__name__)
CORS(app, supports_credentials=True)
config = util.loadConfig()
dt = detection()
sensingdict = dict()

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
        # print(epc)
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

    # for o in objList:
        # epcList = db.mongoHandler.getRelatedTag(o, 'Sensor')
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
    print(state)
    return json.dumps(state)


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
    if util.DEBUG and objName == 'book':
        print(infoList)
    state_list = []
    cnt = 0
    for item in infoList:
        if cnt >= len(epcList):
            break
        sem = db.mongoHandler.getTagSemantic(epcList[cnt], item)
        # if util.DEBUG and objName == 'book':
        #     print(sem)
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
        # 获取phone的状态
        # print('control', sensingdict)
        if phoneEPC in sensingdict.keys():
            phonestatus = sensingdict[phoneEPC]
        else:
            phonestatus = False
        # press event
        dt.updateInteractionEPC(EPClist)
        for event in eventlist:
            if event.is_set():
                # 说明此时有点击事件
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
    r_event = threading.Event()
    r_event.set()
    up_event = threading.Event()
    eventlist = [up_event]

    sonos, bulb = control_init()
    # recvThread = threading.Thread(target=dt.receivedata, args=(config['readerIP'], config['readerPort']))
    # prThread = threading.Thread(target=dt.processdata, args=())

    t1 = threading.Thread(target=dt.detect_status, args=(config['readerIP'], config['readerPort'],r_event,eventlist,))
    resetThread = threading.Thread(target=dt.resetEPC, args=())

    t2 = threading.Thread(target=control_task, args=(sonos,bulb,r_event, eventlist,))

    # recvThread.start()
    # prThread.start()
    t1.start()
    t2.start()
    resetThread.start()
    app.run(port=8888, debug=False, host='0.0.0.0')

