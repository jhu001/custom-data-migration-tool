import json, urllib.request
import os, sys
import asyncio
from datetime import datetime
from progressbar import ProgressBar

parent_dir = os.getcwd()

def readJsonFile(fileName: str):
    with open(fileName, 'r') as f:
        data = json.load(f)
    return data


class migration:
    def __init__(self, originalJson, endPoint, testDataJsonFileName):
        self.jsonFile = originalJson
        self.updatedFile = originalJson.copy()
        self.testDataJsonFileName = testDataJsonFileName
        self.endPoint = endPoint
        self.skippedData = []
        self.processedData = []
        self.mainPath, self.logPath, self.testDataPath = self.createNewWorkspaceFolder()

    def getDocumentIDFromURL(self, url: str):
        try:
            documentID = url.split('-')[-1]
        except Exception as e:
            print(e, " Couldn't' fetch documentID from "+ url)
        if documentID.isnumeric():
            return documentID
        else:
            return None

    def createNewWorkspaceFolder(self):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        mainPath = os.path.join(parent_dir, dt_string)
        logPath = os.path.join(mainPath, 'log')
        testDataPath = os.path.join(mainPath, 'testData')
        os.mkdir(mainPath)
        os.mkdir(logPath)
        os.mkdir(testDataPath)
        return mainPath, logPath, testDataPath
    
    def saveJsonData(self, jsonData, outputPath):
        with open(outputPath, "w") as j:
            json.dump(jsonData, j, indent=2)

    async def createCutomDataDocument(self, data:list):
        dataName = data[0]
        docID = data[1]
        try:
            with urllib.request.urlopen(self.endPoint + docID) as url:
                jsonData = json.loads(url.read().decode())
                if jsonData['status']['code'] != "SUCCESS":
                    self.skippedData.append({dataName: {"reason": "Status != SUCCESS", "data": self.jsonFile[dataName]}})
                    return False
                else:
                    outputPath = os.path.join(self.testDataPath,dataName+"-doc.json")
                    jsonData = jsonData['data']
                    jsonData.pop('url')
                    jsonData.pop('docId')
                    self.saveJsonData(jsonData, outputPath)
                    return True
        except Exception as e:
            e = "HTTPError" if type(e)==urllib.error.HTTPError else e
            self.skippedData.append({dataName: {"reason": e, "data": self.jsonFile[dataName]}})
            return False


    def updatedJson(self):
        pbar = ProgressBar()
        for item in pbar(self.processedData):
            isSuccess = asyncio.run(self.createCutomDataDocument(item))
            if isSuccess:
                dataName = item[0]
                self.updatedFile[dataName]["testData"] = {"document": dataName + "-doc.json"}
        
        updatedJsonDataPath = os.path.join(self.mainPath, "new-"+self.testDataJsonFileName)
        self.saveJsonData(self.updatedFile, updatedJsonDataPath)

        logPath = os.path.join(self.logPath, "logs.json")
        self.saveJsonData(self.skippedData, logPath)
        

    def startMigration(self):
        jsonFile = self.jsonFile
        for item in self.jsonFile:
            if ("url" in jsonFile[item] and not("testData" in self.jsonFile[item])):
                docID = self.getDocumentIDFromURL(jsonFile[item]['url'])
                if (docID != None):
                    self.processedData.append([item, docID])
                else:
                    self.skippedData.append({item: {"reason": "Cant find docID", "data": jsonFile[item]}})
            else:
                self.skippedData.append({item: {"reason": "Couldn't find URL or Custom data already added", "data": jsonFile[item]}})
        self.updatedJson()


def main():
    try:
        args = sys.argv[1:]
        if (len(args) >= 4 and '-url' in args and '-f' in args):
            endPointIndex = args.index('-url') + 1
            testDataJsonFileNameIndex = args.index('-f') + 1
            endPoint = args[endPointIndex] + "/document?url="
            testDataJsonFilePath  = args[testDataJsonFileNameIndex]
            testDataJsonFileName  = testDataJsonFilePath.split("/")[-1]

            # endPoint = "https://selene-lifeco-dev.a-ue1.dotdash.com/document?url="
            # testDataJsonFileName  = 'green-test-data.json'

            jsonDataFile = readJsonFile(testDataJsonFilePath)
            migrator = migration(jsonDataFile, endPoint, testDataJsonFileName)
            migrator.startMigration()
        else:
            print("Input parameters: \n   -url: end point url, eg: https://selene-lifeco-dev.a-ue1.dotdash.com\n   -f: test data file path, eg: ./../green-test-data.json'")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()