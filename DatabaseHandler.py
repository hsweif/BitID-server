import pymongo
import util

class DatabaseHandler:
    def __init__(self):
        config = util.loadConfig()
        host = config['mongoDB']['host']
        port = config['mongoDB']['port']
        dbName = config['mongoDB']['dbName']
        objColName = config['mongoDB']['objCol']
        tagColName = config['mongoDB']['tagCol']
        path = 'mongodb://'+host+':'+str(port)+'/'
        self.client = pymongo.MongoClient(path)
        self.db = self.client[dbName]
        self.objCol = self.db[objColName]
        self.tagCol = self.db[tagColName]
    def insertObject(self, objName):
        newObj = {"name": objName, "RelatedTag": []}
        cnt = 0
        for item in self.objCol.find(newObj):
            cnt = cnt + 1
        if cnt == 0:
            r = self.objCol.insert_one(newObj)
            print(r)
    def getObjects(self):
        objList = []
        for obj in self.objCol.find():
            objList.append(obj["name"])
        return objList
    def getRelatedTags(self, objName):
        item = self.objCol.find_one({"name": objName})
        return item['RelatedTag']
    def insertTag(self, rawData):
        semList = rawData['Semantic']
        self.tagCol.insert_one(rawData)
        if rawData['TagType'] == 'Sensor':
            sem = semList[0]
            name = sem['RelatedObject']
            self.insertObject(name)
            item = self.objCol.find_one({"name": name})
            if item is not None:
                origList = item['RelatedTag']
                if rawData['EPC'] not in origList:
                    origList.append(rawData['EPC'])
                self.objCol.update_one({"name": name}, {"$set": {"RelatedTag": origList}})
    def getTagSemantic(self, epc, state):
        print(epc)
        item = self.tagCol.find_one({"EPC": epc})
        sem = ''
        if item is None:
            return sem
        if state == True: #detected
            sem = item['Semantic'][0]['ON']
        else: #undetected
            sem = item['Semantic'][0]['OFF']
        return sem

mongoHandler = DatabaseHandler()

if __name__ == '__main__':
    mongoHandler.insertTag({"EPC": 'testid2', "TagType": 'Sensor', "Semantic": [{"RelatedObject": "desk1"}]})
    item = mongoHandler.objCol.find_one({"name": "desk1"})
    print(item)