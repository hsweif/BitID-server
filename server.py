from flask import Flask, request
from flask_cors import *
import DataHandler
import queue
import json
import threading
from ObjectHandler import ObjectHandler
from DataHandler import DataHandler

vueUpdateRFIDUrl = 'http://localhost:8000/updateRFID'
interval = 3

app = Flask(__name__)
CORS(app, supports_credentials=True)
q = queue.Queue()
stop = threading.Event()
dataHandler = DataHandler(stop)
objHandler = ObjectHandler()

@app.route('/')
def hello_world():
    return 'hello world'

@app.route('/save-tag', methods=['POST'])
def save_tag():
    content = request.form['content']
    objHandler.saveObject(content)
    return 'success'

@app.route('/update-epc', methods=['GET'])
def update_rfid():
    return dataHandler.getTopTag()

@app.route('/get-objects', methods=['GET'])
def get_objects():
    objList = objHandler.getObjects()
    j = {'objects': test_l}
    return json.dumps(j) 


if __name__ == '__main__':
    dataHandler.start()
    app.run(port=8888, debug=True)
