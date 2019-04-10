import pymongo
import util
from argparse import ArgumentParser
import json
import copy
from bson.objectid import ObjectId
import datetime

class DatabaseHandler:
    def __init__(self):
        config = util.loadConfig()
        host = config['mongoDB']['host']
        port = config['mongoDB']['port']
        dbName = config['mongoDB']['dbName']
        objColName = config['mongoDB']['objCol']
        tagColName = config['mongoDB']['tagCol']
        rawColName = config['mongoDB']['rawCol']
        recgColName = config['mongoDB']['recgCol']
        toggleColName = config['mongoDB']['toggleCol']
        path = 'mongodb://'+host+':'+str(port)+'/'
        self.client = pymongo.MongoClient(path)
        self.db = self.client[dbName]
        self.objCol = self.db[objColName]
        self.tagCol = self.db[tagColName]
        self.togCol = self.db[toggleColName]
        self.rawCol = self.db[rawColName]
        self.recgCol = self.db[recgColName]
        self.updateTag = True 
        self.updateObj = True
        self.relatedTags = {} 
        self.rawToInsert = []
        self.recgToInsert = []
    def insertObject(self, objName):
        self.updateObj = True
        self.updateTag = True
        newObj = {"name": objName, "RelatedSensor": [], "RelatedInteraction": []}
        cnt = 0
        for item in self.objCol.find({"name": objName}):
            cnt = cnt + 1
        if cnt == 0:
            r = self.objCol.insert_one(newObj)
            if util.DEBUG:
                print(r)
    def getObjects(self):
        objList = []
        for obj in self.objCol.find():
            objList.append(obj["name"])
        return objList
    def getMongoData(self, dbName, startTime, endTime):
        db = None
        if dbName == util.TAG:
            db = self.tagCol
        elif dbName == util.OBJECT:
            db = self.objCol
        elif dbName == util.RECG:
            db = self.recgCol
        elif dbName == util.RAW:
            db = self.rawCol
        if db is None:
            return None
        result = []
        startId = ObjectId.from_datetime(generation_time=startTime)
        endId = ObjectId.from_datetime(generation_time=endTime)
        items = db.find({'_id':{'$lt' : endId, '$gte' : startId}})
        for item in items:
            result.append(item)
        return result
    def getToggles(self):
        toggleList = []
        for tog in self.togCol.find():
            toggleList.append(tog["name"])
        return toggleList
    def getToggleControl(self, toggleName):
        ctrList = []
        toggle = self.togCol.find_one({"name": toggleName})
        if toggle is not None:
            ctrList = toggle["control"]
        return ctrList
    def saveRawData(self, rawData):
        tempData = copy.deepcopy(rawData) 
        self.rawToInsert.append(tempData)
        if len(self.rawToInsert) > 1000:
            r = self.rawCol.insert_many(copy.deepcopy(self.rawToInsert))
            self.rawToInsert.clear()
            self.rawToInsert = []
            print(r)
        if util.DEBUG:
            print(rawData)
            print(r)
    def saveRecognized(self, recgData):
        tempData = copy.deepcopy(recgData) 
        self.recgToInsert.append(tempData)
        if len(self.recgToInsert) > 100:
            r = self.recgCol.insert_many(copy.deepcopy(self.recgToInsert))
            self.recgToInsert.clear()
            self.recgToInsert = []
            print(r)
        if util.DEBUG:
            print(r)
    def getRelatedTag(self, objName, kind):
        # if self.updateTag == True or objName not in self.relatedTags.keys():
        item = self.objCol.find_one({"name": objName})
        tagL = []
        if item is None:
            tagL = []
        elif kind != 'Sensor' and kind != 'Interaction':
            tagL = []
        else:
            key = 'Related' + kind # kine: Sensor, Interaction
            tagL = item[key]
        # self.updateTag = False
        # self.relatedTags[objName] = tagL
        return tagL
    def insertTag(self, rawData):
        self.updateTag = True
        r = self.tagCol.insert_one(rawData)
        if util.DEBUG:
            print(r)
        semList = rawData['Semantic']
        tagType = 'Related' + rawData['TagType']
        if rawData['TagType'] == 'Sensor':
            for sem in semList:
                name = sem['RelatedObject']
                if name == '':
                    continue
                self.insertObject(name)
                origList = self.getRelatedTag(name, rawData['TagType'])
                if rawData['EPC'] not in origList:
                    origList.append(rawData['EPC'])
                self.objCol.update_one({"name": name}, {"$set": {tagType: origList}})
        elif rawData['TagType'] == 'Interaction':
            for sem in semList:
                condList = sem['condition']
                for cond in condList:
                    name = cond['object']
                    if name == '':
                        continue
                    self.insertObject(name)
                    origList = self.getRelatedTag(name, rawData['TagType'])
                    if rawData['EPC'] not in origList:
                        origList.append(rawData['EPC'])
                    self.objCol.update_one({"name": name}, {"$set": {tagType: origList}})
                togList = sem['toggle']
                #TODO: Do someting for toggle list
    def getSensorSemantic(self, objName):
        semList = []
        tagList = self.getRelatedTag(objName, util.SENSOR)
        for epc in tagList:
            on_sem = self.getTagSemantic(epc, True)
            off_sem = self.getTagSemantic(epc, False)
            if on_sem != '':
                semList.append(on_sem)
            if off_sem != '':
                semList.append(off_sem)
        return semList
    def getTagSemantic(self, epc, state):
        # if util.DEBUG:
        #     print(epc)
        item = self.tagCol.find_one({"EPC": epc, "TagType": "Sensor"})
        sem = ''
        if item is None:
            return sem
        if state == True: #detected
            sem = item['Semantic'][0]['ON']
        else: #undetected
            sem = item['Semantic'][0]['OFF']
        return sem
    def removeObject(self, objName):
        # TODO: Should I support the relevent removal from Interaction condition?
        item = mongoHandler.objCol.find_one({"name": objName})
        if item is None:
            print('The object is not found.')
            return
        tagList = []
        for tag in item['RelatedSensor']:
            tagList.append(tag)
        for tag in item['RelatedInteraction']:
            tagList.append(tag)
        for tag in tagList:
            self.tagCol.delete_many({"EPC": tag})
        self.objCol.delete_many({"name":objName})
    def PKTime(self, year, month, day, hour, minute, sec):
        return datetime.datetime(year, month, day, hour - 8, minute, sec)
    def timeStamp2Datetime(self, timeStamp):
        d = datetime.datetime.fromtimestamp(timeStamp)
        str1 = d.strftime("%Y-%m-%d %H:%M:%S.%f")
        print(str1)
        # 2015-08-28 16:43:37.283000'
        return d 


mongoHandler = DatabaseHandler()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-m", "--mode", help="[delete, toggle]", dest="mode", required=True)

    args = parser.parse_args()
    if args.mode == 'toggle':
        print('This is the interaction mode to set up toggle meaning')
        while True:
            objName = input('Please input the object name. Empty to exit:\n')
            if objName == '':
                break
            semList = []
            print('Please input the controllable action. Left empty means finish adding:')
            while True:
                sem = input('One another control action:\n')
                if sem == '':
                    break
                semList.append(sem)
            item = mongoHandler.togCol.find_one({"name": objName})
            print(item)
            if item is None:
                mongoHandler.togCol.insert_one({"name": objName, "control": []})
                item = mongoHandler.togCol.find_one({"name": objName})
            origList = item["control"]
            for s in semList:
                origList.append(s)
            if util.DEBUG:
                print(origList)
            mongoHandler.togCol.update_one({"name": objName}, {"$set": {"control": origList}})
    elif args.mode == 'delete':
        print('This is the interaction mode to delete an object. The object you input and its related tags will be deleted.')
        while True:
            objName = input('Please input the object name. Empty to exit:\n')
            if objName == '':
                break
            mongoHandler.removeObject(objName)
    elif args.mode == 'mongotest':
        t = mongoHandler.timeStamp2Datetime(1554791393)
        start_time = mongoHandler.PKTime(2019, 4, 8, 0, 0, 0)
        end_time = mongoHandler.PKTime(2020, 3, 28, 0, 0, 0)
        result = mongoHandler.getMongoData(util.OBJECT, startTime=start_time, endTime=end_time)
        print(result)
            
