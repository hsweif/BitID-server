import socket
import util
import re
import os
import time
from datetime import datetime, timedelta
import threading

class DataHandler(threading.Thread):
    def __init__(self, stop_event):
        threading.Thread.__init__(self)
        self._stop = stop_event
        self.xInput = {}
        self.threshold = 100
        config = util.loadConfig()
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = config['readerIP']
        self.port = config['readerPort']
        self.maxRSSI = 0
        self.maxEPC = ''
        self.bufSize = 2048
        try:
            self.s.connect((self.host, self.port))
        except BlockingIOError:
            pass
        resetThread = threading.Thread(target=self.resetEPC, args=())
        resetThread.start()
    def resetEPC(self):
        while True:
            self.maxRSSI = 0
            self.maxEPC = ''
            time.sleep(1)
    def updateEPC(self, rssi, epc):
        if rssi > self.maxRSSI:
            self.maxEPC = epc
    def getTopTag(self):
        return 'ONLY for testing'
        if self.maxRSSI > self.threshold:
            return self.maxEPC 
        else:
            return None
    def run(self):
        # TODO: 改成从config读取
        first_number = ''
        while True:
            data = self.s.recv(self.bufSize).decode()
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
                            self.updateEPC(self.xInput['RSSI'], self.xInput['EPC'])
                        i += 1
            else:
                break

