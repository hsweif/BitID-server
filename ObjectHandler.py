import os
import json
import util

class ObjectHandler():
    def __init__(self):
        self.objects = {} 
        self.config = util.loadConfig()
    def getObjects(self):
        objList = ['test1', 'test2']
        return objList
    def saveObject(self, newObj):
        # TODO: Save object to mongodb
        print(newObj)
        # fileName = newObj['objName']
        # if fileName not in self.objects.keys:
        #     with open(fileName+'.json', 'w') as f:
        #         json.dump(newObj, f)
        #     self.objects[fileName] = newObj
        # else:
        #     self.objects[fileName]
