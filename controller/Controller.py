import time

from view.View import View
from controller.Config import Config
from controller.ViscaOverIPService import ViscaOverIPService
from controller.AxisState import AxisState

class Controller:

    PANAXIS = AxisState()
    TILTAXIS = AxisState()
    ZOOMAXIS = AxisState()

    #initialize the variables so that they are set
    config = {}
    debug = False

    def __init__(self):
        super().__init__()

        #load the configuration from the app.conf file
        self.loadConfig()

        #set up the network service so that we can
        # communicate with the cameras
        self.setupViscaOIPService()

        #setup and load the UI
        self.setupUI()

    def loadConfig(self):
        #create a config object and load the
        #config from the app.conf file
        self.config = Config()
        self.debug = self.config.debugIsEnabled()

    def setupViscaOIPService(self):
        #create the server
        self.ViscaOverIPService = ViscaOverIPService(self.config.getNetworkConfig(), self.debug)
    
    def setupUI(self):
        #setup a subset of the config
        #we don't need to pass the entire config
        viewConfig = {
            "debug": self.config.debugIsEnabled(),
            "ui": self.config.getUIConfig(),
            "camera": self.config.getCameraConfig(),
            "joystick": self.config.getJoystickConfig()
        }

        #callback Function list - this provides all the actions
        #for the button clicks and UI Interactions
        #we want to bring the business logic back out to the Controller,
        #so we are giving the View the callback functions to use
        viewActions = {
            "sendCommand": self.sendCommand,
            "presetSave": self.presetSaveClick,
            "close": self.quit
        }

        #create the UI QT object
        self.view = View(viewConfig, viewActions)
        
    def start(self):
        self.view.start(self.config.getUIConfig()["fullscreen"])
    
    def quit(self, event):
        self.ViscaOverIPService.closeUDPServer()
    
    #Action for clicking a button to switch cameras
    # def cameraClick(self, command, selectedCameraInfo):
    #     self.sendCommand(command, selectedCameraInfo)
    
    # def ptzPressed(self, command, selectedCameraInfo):
    #     self.sendCommand(command, selectedCameraInfo)
    
    # def ptzReleased(self, command, selectedCameraInfo):
    #     self.sendCommand(command, selectedCameraInfo)
    
    # def presetClick(self, command, selectedCameraInfo):
    #     self.sendCommand(command, selectedCameraInfo)
    
    def sendCommand(self, command):
        #try and send the command, but if it fails,
        #reset the sequence number and move on
        self.ViscaOverIPService.sendUDPMessage(command)
        
    def presetSaveClick(self, button, selectedCameraInfo):
        #logic for saving presets and reloading locations
        #first I need to get the current location of the camera

        currentPosition = {
            "pan": [],
            "tilt": [],
            "zoom": []
        }

        response = self.ViscaOverIPService.sendUDPMessage("INQPT", selectedCameraInfo)
        if(response != None):
            currentPosition["pan"] = response.getPayload()[2:4]
            currentPosition["tilt"] = response.getPayload()[6:4]
        
        response = self.ViscaOverIPService.sendUDPMessage("INQZOOM", selectedCameraInfo)
        if(response != None):
            currentPosition["zoom"] = response.getPayload()[2:4]

        if self.debug:
            print("PAN: ", currentPosition["pan"])
            print("TILT: ", currentPosition["tilt"])
            print("ZOON: ", currentPosition["zoom"])
        
        #save the position in memory for now
        button.presetInfo["panPosition"] = currentPosition["pan"]
        button.presetInfo["tiltPosition"]  = currentPosition["tilt"]
        button.presetInfo["zoomPosition"] = currentPosition["zoom"]
        button.presetInfo["command"] = "PresetPanTilt"

        self.config.updatePreset(button.presetInfo, button.id, selectedCameraInfo["id"])



    # def joystickUIButtonClicked(self, checked):
    #     if(checked):
    #         #close any previously open joystick.
    #         if hasattr(self, "joystick"):
    #             self.joystick.close()

    #         #set up a new instance of the joystick object
    #         self.joystick = Joystick(self.config.getJoystickConfig(), self.debug, axesAction = self.joystickAxesAction, buttonAction = self.joystickButtonActionDown)
        
    #         #Check if there are any joysticks connected... 
    #         # if so start receiving joystick events
    #         # if not, just uncheck the joystick button on the UI
    #         if(self.joystick.detectedJoysticks()):
    #             self.joystick.start()
    #         else:
    #             if self.debug:
    #                 print("No detected Joysticks")
    #             self.view.joystickButton.setChecked(False)
    #     else:
    #         if hasattr(self, "joystick"):
    #             self.joystick.close()

    #         if self.debug:
    #             print("Disabled joysticks")   

    #         self.view.joystickButton.setChecked(False)

    # def joystickButtonActionDown(self, buttonData):
    #     #a button has been pressed
    #     #go through each button

    #     for actiontype, data in self.config["joystick"].items():
    #         if data["type"] == "button" and data["id"] == buttonData.button:
    #             currentButtonId = self.view.getSelectedCameraId()
    #             totalCameras = len(self.config["cameras"])
    #             newButtonId = (currentButtonId + 1) % totalCameras
    #             self.view.getCameraButton(newButtonId).click()
  
    # def joystickAxesAction(self, axesData):
    #     #the Axes have changed
    #     #go through each configured axis...
    #     #get the Axis that is related
        
    #     for actiontype, data in self.config["joystick"].items():
    #         if data["type"] == "axis" and data["id"] == axesData.axis:
    #             newValue = round(axesData.value * self.MAXSPEED[actiontype])

    #             theAxis = self.getAxisStateByName(actiontype)
    #             #we can't zoom and pan/tilt at the same time, so make sure that we only do one at a time
    #             #zoom will be secondary and only function if we are already not panning or tilting
    #             if actiontype == "zoom":
    #                 if not (self.PANAXIS.isActive() or self.TILTAXIS.isActive()):
    #                     #only update the zoom value if not panning or tilting
    #                     # self.ptzChangeSpeed(actiontype, abs(newValue))
    #                     if(theAxis.getRawVector() == newValue):
    #                         return
    #                     else:
    #                         theAxis.setRawVector(newValue)
    #                         if newValue > 0:
    #                             theAxis.setHigh() 
    #                             if self.debug:
    #                                 print("Zooming Out at speed ", theAxis.getVector())
    #                             self.ViscaOverIPService.sendUDPMessage("ZoomWide", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "zoom": theAxis.getVector()}})
    #                         elif newValue < 0:
    #                             theAxis.setLow()
    #                             if self.debug:
    #                                 print("Zooming In at speed ", theAxis.getVector())
    #                             self.ViscaOverIPService.sendUDPMessage("ZoomTele", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "zoom": theAxis.getVector()}})
    #                         else:
    #                             theAxis.unset()
    #                             if self.debug:
    #                                 print("Stopped Zooming", theAxis.getVector())
    #                             self.ViscaOverIPService.sendUDPMessage("ZoomStop", self.view.getSelectedCameraButton().cameraInfo)      
    #             else:
    #                 #we are panning and tilting
    #                 if not (self.ZOOMAXIS.isActive()):
    #                     #go ahead... pan and tilt
    #                     # self.ptzChangeSpeed(actiontype, abs(newValue))
    #                     if(theAxis.getRawVector() == newValue):
    #                         return
    #                     else:
    #                         theAxis.setRawVector(newValue)
    #                         if newValue < 0:
    #                             theAxis.setLow()
    #                         elif newValue > 0:
    #                             theAxis.setHigh()
    #                         elif newValue == 0:
    #                             theAxis.unset()
                                                    
    #                         if self.PANAXIS.isActive() and self.TILTAXIS.isInactive():
    #                             #Only the PAN AXIS is activated
    #                             if(self.PANAXIS.isLow()):
    #                                 if self.debug:
    #                                     print("Panning Left at Speed ", self.PANAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("PanLeft", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                             else:
    #                                 #it must be low since it is inactive
    #                                 if self.debug:
    #                                     print("Panning Right at Speed ", self.PANAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("PanRight", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                         elif self.PANAXIS.isInactive() and self.TILTAXIS.isActive():
    #                             #Only the TILT axis is active
    #                             if self.TILTAXIS.isLow():
    #                                 if self.debug:
    #                                     print("Tilting Up at Speed ", self.TILTAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("TiltUp", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                             else:
    #                                 if self.debug:
    #                                     print("Tilting Down at Speed ", self.TILTAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("TiltDown", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                         elif self.PANAXIS.isActive() and self.TILTAXIS.isActive():
    #                             #both PAN and TILT are active
    #                             if self.PANAXIS.isLow() and self.TILTAXIS.isLow():
    #                                 if self.debug:
    #                                     print("Tilting Up+Left at Speed ", self.PANAXIS.getVector(), self.TILTAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("PanTiltUpLeft", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                             elif self.PANAXIS.isLow() and self.TILTAXIS.isHigh():
    #                                 if self.debug:
    #                                     print("Tilting Down+Left at Speed ", self.PANAXIS.getVector(), self.TILTAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("PanTiltDownLeft", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                             elif self.PANAXIS.isHigh() and self.TILTAXIS.isLow():
    #                                 if self.debug:
    #                                     print("Tilting Up+Right at Speed ", self.PANAXIS.getVector(), self.TILTAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("PanTiltUpRight", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                             elif self.PANAXIS.isHigh() and self.TILTAXIS.isHigh():
    #                                 if self.debug:
    #                                     print("Tilting Down+Right at Speed ", self.PANAXIS.getVector(), self.TILTAXIS.getVector())
    #                                 self.ViscaOverIPService.sendUDPMessage("PanTiltDownLeft", self.view.getSelectedCameraButton().cameraInfo, {"speed": { "pan": self.PANAXIS.getVector(),"tilt": self.TILTAXIS.getVector()}})
    #                         else:
    #                             #neither are active
    #                             if self.debug:
    #                                 print("Stopping PAN/TILT", self.PANAXIS.getVector(), self.TILTAXIS.getVector())
    #                             self.ViscaOverIPService.sendUDPMessage("PanTiltStop", self.view.getSelectedCameraButton().cameraInfo)

    
    # def getAxisStateByName(self, name):
    #     if name == "pan":
    #         return self.PANAXIS
    #     elif name == "tilt":
    #         return self.TILTAXIS
    #     elif name == "zoom":
    #         return self.ZOOMAXIS
    #     else:
    #         return None