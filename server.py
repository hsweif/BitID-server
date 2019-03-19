from flask import Flask, request
from flask_cors import *
import DataHandler
import queue
import json
import threading
import DatabaseHandler as db
from DataHandler import DataHandler

vueUpdateRFIDUrl = 'http://localhost:8000/updateRFID'
interval = 3

app = Flask(__name__)
CORS(app, supports_credentials=True)
q = queue.Queue()
stop = threading.Event()
dataHandler = DataHandler(stop)

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
def update_rfid():
    return dataHandler.getTopTag()

@app.route('/get-objects', methods=['GET'])
def get_objects():
    objList = db.mongoHandler.getObjects()
    j = {'objects': objList}
    return json.dumps(j) 

@app.route('/get-object-state', methods=['POST'])
def get_object_state():
    objName = request.form['objName']
    infoList = dataHandler.getTagState(objName)
    j = {'info': infoList}
    return json.dumps(j) 

if __name__ == '__main__':
    dataHandler.start()
    app.run(port=8888, debug=True)
