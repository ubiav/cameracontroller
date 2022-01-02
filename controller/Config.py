import os, json

class Config:
    def __init__(self):
        super().__init__()
        
        self.APP_CONF = "conf/app.conf"
        self.APP_DIR = os.getcwd()
        self.loadConfig()
    
    def loadConfig(self):
        self.config = self.getFileContentsAsJSON(self.APP_DIR + "/" + self.APP_CONF)
    
    def saveConfig(self):
        self.saveFileContentsAsJSON(self.APP_DIR + "/" + self.APP_CONF + "_new")

    def getFileContentsAsJSON(self, filename, mode = "r"):
        file = open(filename, mode)
        contents = file.read()
        jsonContents = json.loads(contents)
        file.close()
        return jsonContents
    
    def saveFileContentsAsJSON(self, filename, mode = "w"):
        file = open(filename, mode)
        jsonData = json.dumps(self.config)
        file.write(jsonData)
        file.close()
    
    def getConfig(self):
        return self.config

    def getGeneralConfig(self):
        return self.config["general"]

    def debugIsEnabled(self):
        return self.getGeneralConfig()["debug"]

    def getUIConfig(self):
        return self.config["ui"]
    
    def getNetworkConfig(self):
        return self.config["network"]

    def getCameraConfig(self):
        return self.config["cameras"]
    
    def getCameraCount(self):
        return len(self.getCameraConfig())
    
    def getDefaultCamera(self):
        cameras = self.getCameraConfig()
        for camera in cameras:
            if(camera["default"]):
                return cameras.index(camera)
        return None

    def getJoystickConfig(self):
        return self.config["joystick"]
    
    def updatePreset(self, updateData, presetIndex, cameraIndex):
        self.config["cameras"][cameraIndex]["presets"][presetIndex] = updateData
        self.saveConfig()
