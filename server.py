import argparse
import socket
import threading
from threading import Timer
import queue
import requests
from flask import Flask, request
from flask_cors import *


vueUpdateRFIDUrl = 'http://localhost:8000/updateRFID'
interval = 3

class TagReader(threading.Thread):
    def __init__(self, stop_event, host, port, buf_size=512):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.stopped = stop_event
        self.buf_size = buf_size
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.host, self.port))
        except BlockingIOError:
            pass
        print('connected: ' + str(self.s))

    def run(self):
        while not self.stopped.is_set():
            try:
                data = self.s.recv(self.buf_size).decode('utf-8')
                print(data)
            except(socket.error, IndexError, ValueError) as e:
                print(e)
                continue
        self.s.close()


candidateList = [1,2,3]

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():
    return 'hello world'

@app.route('/save-tag', methods=['POST'])
def save_tag():
    print('save-tag')
    print(request.form)
    content = request.form['content']
    print(content)
    return 'success'

@app.route('/update-epc', methods=['GET'])
def update_rfid():
    # TODO: Implement here
    global candidateList
    epcList = {'epc': candidateList}
    return str(epcList) 

class DataPreprocess():
    def __init__(self):
        self.xInput = {}
        self.threshold = 100
    def continuousRead(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # TODO: 改成从config读取
        s.connect(('192.168.53.131',14))
        first_number = ''
        global candidateList
        while True:
            data = s.recv(2048).decode()
            if data:
                # 处理不完整的信息
                data = first_number + data
                first_number = ''
                while not  data[-1:] == '\n':
                    first_number = data[-1:] + first_number
                    data =  data[:-1]

                datalist = re.split('[,;]', data)
                i = 0
                for item in datalist:
                    k = i % 9
                    if item == '':
                        continue
                    else:
                        if k  ==  1:
                            self.xInput['EPC'] = item
                        elif k == 2:
                            self.xInput['Antenna'] = int(item)
                        elif k == 3:
                            self.xInput['Freq'] = float(item)
                        elif k == 4:
                            self.xInput['ReaderTimestamp'] = timedelta(seconds = (float(item)/1000))
                        elif k == 5:
                            self.xInput['RSSI'] = float(item)
                        elif k == 6:
                            self.xInput['Doppler'] = float(item)
                        elif k == 7:
                            self.xInput['Phase'] = float(item)
                        elif k == 8:
                            self.xInput['ComputerTimestamp'] = timedelta(seconds = (float(item[:-1])/1000))
                        else:
                            if(self.xInput['RSSI'] > self.threshold):
                                candidateList.append(self.xInput['EPC'])
                        i += 1
            else:
                break
            # print(self.xInput)
            

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--port", "-p", dest="port", default=14, type=int, help="Port")
    # parser.add_argument("--host", dest="host", default="localhost", type=str, help="Host IP")
    # args = parser.parse_args()
    # HOST = args.host
    # PORT = args.port
    # print("Server start...")
    # q = queue.Queue()
    # stop = threading.Event()
    # tag_reader = TagReader(stop, HOST, PORT, 512)
    # tag_reader.start()
    app.run(port=8888, debug=True)

        
