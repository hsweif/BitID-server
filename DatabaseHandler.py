import pymongo
import util

class DatabaseHandler:
    def __init__(self):
        config = util.loadConfig()
        host = config['mongoDB']['host']
        port = config['mongoDB']['port']
        dbName = config['mongoDB']['dbName']
        objColName = config['mongoDB']['objCol']
        path = 'mongodb://'+host+':'+str(port)+'/'
        self.client = pymongo.MongoClient(path)
        self.db = self.client[dbName]
        self.objCol = self.db[objColName]
    def insertObject(self, objName):
        newObj = {"name": objName}
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
    def insertTag(self, rawData):
        semList = rawData['semantic']
        if rawData['TagType'] == 'Sensor':
            sem = semList[0]
            name = sem['RelatedObject']
            self.insertObject(name)

mongoHandler = DatabaseHandler()
mongoHandler.insertObject('testObj')