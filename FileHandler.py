import re
import os
from argparse import ArgumentParser

defaultstatus = {'drawer2':True, 'drug bottle':False, 'cup':True, 'book':False, 'phone':False, 'box':False, 'charger':True}
interactionList = ['light', 'music']
objListA = ['drawer2', 'drug bottle', 'cup', 'cup', 'drug bottle', 'drawer2']
statusListA = [False, True, False, True, False, True]
objListB = ['light', 'book', 'book', 'light']
statusListB = [None, True, False, None]
objListC = ['phone', 'music', 'music', 'phone']
statusListC = [True, None, None, False]
objListD = ['box', 'box', 'charger', 'charger']
statusListD = [True, False, False, True]
eventlist = list()
for i in range(0, 4):
    eventlist.append(list())

mileStone1 = []
mileStone2 = []
mileStone3 = []
mileStone4 = []
allEvent = []

class info:
    def __init__(self, objName, status, timeStamp=None):
        self.timeStamp = timeStamp
        self.objName = objName
        self.status = status 

def initEvent():
    global mileStone1
    global mileStone2
    global mileStone3
    global mileStone4
    cnt = 0
    for (objList, statusList) in [(objListA, statusListA),(objListB, statusListB),(objListC, statusListC),(objListD, statusListD)]: 
        for i in range(0, len(objList)):
            ifo = info(objList[i], statusList[i])
            eventlist[cnt].append(ifo)
        cnt = cnt+1
    mileStone1 = eventlist[0]+eventlist[1]+eventlist[2]+eventlist[3]
    mileStone2 = eventlist[1]+eventlist[0]+eventlist[3]+eventlist[2]
    mileStone3 = eventlist[2]+eventlist[3]+eventlist[0]+eventlist[1]
    mileStone4 = eventlist[3]+eventlist[2]+eventlist[1]+eventlist[0]
    for mStone in [mileStone1, mileStone2, mileStone3, mileStone4]:
        for item in mStone:
            allEvent.append(item)

def processCSV(origCSV):
    infoList = []
    stampList = []
    with open(origCSV, 'r') as f:
        timeStamp = ''
        flag = False
        for line in f.readlines():
            if flag == False:
                flag = True
            else:
                timeStamp = line
                flag = False
                timeStamp = timeStamp.strip('\n')
                for ts in re.split(',', timeStamp):
                    stampList.append(ts)
    if len(stampList) != len(allEvent):
        print("[ERROR] The number of time stamp cannot match the number of event!")
        print("Time stamp list size:" + str(len(stampList)))
        print("Event list size:" + str(len(allEvent)))
        return

    for i in range(0, len(stampList)):
        allEvent[i].timeStamp = stampList[i]

    stateDict = dict() 
    nameList = list() 
    for item in mileStone1:
        if item.status == None:
            continue
        if item.objName not in stateDict.keys():
            nameList.append(item.objName)
            stateDict[item.objName] = item.status
    with open(origCSV+'_converted.csv', 'w') as f:
        for name in nameList:
            f.write(','+name)
        f.write('\n')
        for e in allEvent:
            f.write(e.timeStamp)
            if e.status != None:
                stateDict[e.objName] = e.status
            for name in nameList:
                f.write(',' + str(stateDict[name]))
            f.write('\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-s", "--src", dest="fileName", help="The file you want to transfer.", required=True)
    args = parser.parse_args()
    fileName = args.fileName
    if not os.path.exists(fileName):
        print("[ERROR] File path doesn't exist")
        exit()
    initEvent()
    # processCSV('./data/2018310831.csv')
    processCSV(fileName)
    print("finished!")
 