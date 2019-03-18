import json

def loadConfig():
    with open('./config.json', 'r') as f:
        content = json.load(f)
    return content

def filtFileName(rawName, kind='JSON'):
    '''
    A util function just used for make objname.json to objname. Default file type is json
    '''
    l = len(kind) + 1
    return rawName[:-l]
