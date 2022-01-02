from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QButtonGroup, QSlider, QInputDialog
from PyQt5.QtCore import Qt
from view.Joystick import Joystick

class View(QMainWindow) : 

    #button styles and coloring
    cssStyles = {
        "cameras": {
            "selected": "border: 1px solid darkgreen; background-color: green; color: white",
            "unselected": "border: 1px solid black; background-color: white; color: black",
            "disabled": "border: 1px solid darkgrey; background-color: grey; color: black"          
        },
        "ptz": {
            "selected": "border: 1px solid orange; background-color: darkorange; color: white",
            "unselected": "border: 1px solid black; background-color: white; color: black",          
            "disabled": "border: 1px solid darkgrey; background-color: grey; color: black"          
        },
        "ptzSlider": {
            "enabled": "color: white",     
            "disabled": "color: black"          
        },
        "presets": {
            "selected": "border: 1px solid blue; background-color: darkblue; color: white",
            "unselected": "border: 1px solid black; background-color: white; color: black",
            "disabled": "border: 1px solid darkgrey; background-color: grey; color: black"          
        },
        "presetSave": {
            "selected": "border: 1px solid darkred; background-color: red; color: white",
            "unselected": "border: 1px solid black; background-color: lightgray; color: black",
            "disabled": "border: 1px solid darkgrey; background-color: grey; color: black"          
        },
        "joystick": {
            "selected": "border: 1px solid darkgreen; background-color: lightgreen; color: black",
            "unselected": "border: 1px solid black; background-color: lightgray; color: black",         
            "disabled": "border: 1px solid darkgrey; background-color: grey; color: black"          
        }
    }

    def __init__(self, config, actions):
        super().__init__()
        self.uiConfig = config["ui"]
        self.cameraConfig = config["camera"]
        self.joystickConfig = config["joystick"]
        self.debug = config["debug"]
        self.actionHandlers = actions
        self.joystick = None
        self.closeEvent = self.quit
        self.initWindow()

        #set up the camera buttons if they are configured
        if(len(self.cameraConfig) > 0):
            #initialize the camera buttons
            self.initCameraButtons()
        
        self.initPTZButtons()

        self.initSavePresetButton()
        
        self.initJoystickUIButtons()
        self.initJoystickControl()

        #Now that everything has been set up, let's show the UI
        if self.uiConfig["fullscreen"]:
            self.showFullScreen()
        else:
            self.show()
        
    def quit(self, event):
        self.closeJoystickControl()        
        self.actionHandlers["close"](event)

    def initWindow(self) : 
        self.move(0,0)
        self.resize(self.uiConfig["windowWidth"], self.uiConfig["windowHeight"])
        self.setWindowTitle('Tomball Stake Camera Control Systems')

        if(self.uiConfig["backgroundImage"] != "") :
            mainStyleSheet = "View { background-image: url(" + self.uiConfig["backgroundImage"] + "); background-repeat: no-repeat; }"
            self.setStyleSheet(mainStyleSheet)

        mainTitle = QLabel(self)
        mainTitle.setText("<font style='color: white; font-size: 16pt;'><i><b>Tomball Stake Camera Control System</b></i></font>")
        mainTitle.move(345, 430)
        mainTitle.resize(450,30)
    
    def initCameraButtons(self) :

        def camButtonToggled(camera, state):
            #handle all the UI stuff here
            if(state):                
                self.selectCameraButton(camera)

                #now call the controller action to allow the Controller
                #to perform business logic based on the button click
                command = {"command": "SEQNO_RESET", "cameraInfo": camera.cameraInfo}
                self.actionHandlers["sendCommand"](command)
            else:
                self.unselectCameraButton(camera)
     
        cameraSelectTitle = QLabel(self)
        cameraSelectTitle.setText("<font style='color: white; font-size: 12pt;'>Camera Select</font>")
        cameraSelectTitle.move(15, 15)
        cameraSelectTitle.resize(450,30)

        camButtons = QButtonGroup(self)
        camButtons.buttonToggled.connect(camButtonToggled)

        startCamX = 15
        startCamY = 50

        cameraDefault = None

        for camButton in self.cameraConfig :
            newButton = QPushButton(camButton["text"], self)
            camButton["id"] = self.cameraConfig.index(camButton)
            newButton.cameraInfo = camButton
            newButton.presetButtonGroup = self.initPresetButtons(camButton)
            newButton.flat = True
            newButton.resize(75,75)
            newButton.move(startCamX,startCamY)
            newButton.setCheckable(True)
            newButton.setDefault(False)
            newButton.setStyleSheet(self.cssStyles["cameras"]["unselected"])
            startCamX += 85
            camButtons.addButton(newButton, camButton["id"])

            #click the button, if the camera is the default
            if(camButton["default"]):
                cameraDefault = camButton["id"]
        
        self.cameraButtons = camButtons

        #click the default camera button to activate it
        defaultCamButton = self.getCameraButton(cameraDefault)
        defaultCamButton.click()          
    
    def selectCameraButton(self, cameraId):
        camButton = self.getCameraButton(cameraId)

        #if the camButton is a real object,
        #then go ahead and select it
        if(camButton != None):
            for presetButton in camButton.presetButtonGroup.buttons():
                presetButton.setVisible(True)
            camButton.setStyleSheet(self.cssStyles["cameras"]["selected"])
            camButton.repaint()

            if self.debug:
                print("Camera ", camButton.cameraInfo["id"] + 1, " selected")
            
    def unselectCameraButton(self, cameraId):
        camButton = self.getCameraButton(cameraId)

        #if the camButton is a real object,
        #then go ahead and unselect it
        if(camButton != None):
            for presetButton in camButton.presetButtonGroup.buttons():
                presetButton.setVisible(False)
            camButton.setStyleSheet(self.cssStyles["cameras"]["unselected"])
    
    def getCameraButton(self, cameraId):
        return self.getQPushButtonFromButtonGroup(self.cameraButtons, cameraId)
    
    def getSelectedCameraButton(self):
        return self.getCameraButton(self.getSelectedCameraId())
    
    def getSelectedCameraId(self):
        return self.cameraButtons.checkedId()

    def selectNextCamera(self):
        nextCamera = False
        cameraFound = False
        selectedCamera = self.getSelectedCameraButton()
        for cameraButton in self.cameraButtons.buttons():
            if cameraButton == selectedCamera:
                nextCamera = True
            elif nextCamera:
                cameraFound = True
                cameraButton.click()
        
        #we've gotten to the end of the list and the last camera
        #is the currently selected one.  So loop around to the start
        #of the list and select the first camera
        if(nextCamera and not cameraFound):
            self.cameraButtons.buttons()[0].click()

    def initPTZButtons(self):
        
        def speedChange(value):
            if self.debug:
                print("Speed Change: ", value)

        def ptzPressed(button):
            if self.debug:
                print("PTZ pressed", button.action)
            
            self.activatePTZButton(button)
            
            command = {
                "command": button.action,
                "extraData": {"speed": self.getPTZSpeeds()},
                "cameraInfo": self.getSelectedCameraButton().cameraInfo
            }
            self.actionHandlers["sendCommand"](command)

        def ptzReleased(button):
            if self.debug:
                print("PTZ released", button.stopAction)
            
            command = {
                "command": button.stopAction,
                "cameraInfo": self.getSelectedCameraButton().cameraInfo
            }
            self.actionHandlers["sendCommand"](command)
            self.deactivatePTZButton(button)

        def getNewButton(label, buttonInfo): 
            newButton = QPushButton(label, self)
            newButton.flat = True
            newButton.resize(75,75)
            newButton.setStyleSheet(self.cssStyles["ptz"]["unselected"])
            newButton.action=buttonInfo[0]
            newButton.stopAction=buttonInfo[1]
            newButton.move(buttonInfo[2], buttonInfo[3])
            return newButton
        
        def getNewSlider(label, buttonInfo):
            sTitle = QLabel(self)
            sTitle.setText("<font style='color: white; font-size: 9pt;'>" + buttonInfo["label"][0] + "</font>")
            sTitle.move(buttonInfo["label"][1], buttonInfo["label"][2])
            sTitle.resize(80, 18)
            setattr(self, label + "Label", sTitle)

            slider = QSlider(Qt.Orientation.Horizontal, self)
            slider.move(buttonInfo["slider"][2], buttonInfo["slider"][3])

            #should the slider be horizontal or not?
            if(buttonInfo["slider"][4]):
                slider.resize(100,25)
            else:
                slider.resize(25,75)
                slider.setOrientation(Qt.Vertical)

            slider.setMinimum(0)
            slider.setMaximum(buttonInfo["slider"][1])
            slider.setValue(buttonInfo["slider"][0])
            slider.valueChanged.connect(speedChange) 
            slider.setMinimumHeight(30)
            slider.setMinimumWidth(30)
            setattr(self, label + "Speed", slider)


        ptzTitle = QLabel(self)
        ptzTitle.setText("<font style='color: white; font-size: 12pt;'>Pan / Tilt / Zoom</font>")
        ptzTitle.move(15, 150)
        ptzTitle.resize(250,30)

        self.ptzButtons = QButtonGroup(self)
        self.ptzButtons.buttonPressed.connect(ptzPressed)
        self.ptzButtons.buttonReleased.connect(ptzReleased)

        ptzButtonDefs = {
            "Up": [ "TiltUp", "PanTiltStop", 100, 190 ],
            "Down": [ "TiltDown", "PanTiltStop", 100, 275 ],
            "Left": [ "PanLeft", "PanTiltStop", 15, 223 ],
            "Right": [ "PanRight", "PanTiltStop", 185, 223 ],
            "Zoom In": ["ZoomTele", "ZoomStop", 270, 190],
            "Zoom Out": ["ZoomWide", "ZoomStop", 270, 275]
        }

        ptzSliderDefs = {
            "pan": {
                "label": ["Pan Speed", 110, 360],
                "slider": [self.uiConfig["speeds"]["default"]["pan"], self.uiConfig["speeds"]["max"]["pan"] , 85, 380, True]
            },
            "tilt": {
                "label": ["Tilt Speed", 195, 340],
                "slider": [self.uiConfig["speeds"]["default"]["tilt"], self.uiConfig["speeds"]["max"]["tilt"], 210, 365, False]
            },
            "zoom": {
                "label": ["Zoom Speed", 275, 360],
                "slider": [self.uiConfig["speeds"]["default"]["zoom"], self.uiConfig["speeds"]["max"]["zoom"] , 255, 380, True]
            }
        }

        for name in ptzButtonDefs:
            self.ptzButtons.addButton(getNewButton(name, ptzButtonDefs[name]))

        for name in ptzSliderDefs:
            getNewSlider(name, ptzSliderDefs[name])
    
    def activatePTZButton(self, buttonId):
        ptzButton = self.getPTZButton(buttonId)
        if ptzButton != None:
            ptzButton.setStyleSheet(self.cssStyles["ptz"]["selected"])
            ptzButton.repaint()

    def deactivatePTZButton(self, buttonId):
        ptzButton = self.getPTZButton(buttonId)
        if ptzButton != None:
            ptzButton.setStyleSheet(self.cssStyles["ptz"]["unselected"])
            ptzButton.repaint()
    
    def getPTZButton(self, buttonId):
        return self.getQPushButtonFromButtonGroup(self.ptzButtons, buttonId)
    
    def getPTZButtonId(self, button):
        return self.ptzButtons.id(button)

    def getPanSpeed(self):
        return self.panSpeed.value()

    def setPanSpeed(self, panSpeed):
        self.panSpeed.setValue(panSpeed)
    
    def getTiltSpeed(self):
        return self.tiltSpeed.value()

    def setTiltSpeed(self, tiltSpeed):
        self.panSpeed.setValue(tiltSpeed)

    def getZoomSpeed(self):
        return self.zoomSpeed.value()

    def setZoomSpeed(self, zoomSpeed):
        self.panSpeed.setValue(zoomSpeed)
    
    def getPTZSpeeds(self):
        return {
            "pan": self.getPanSpeed(),
            "tilt": self.getTiltSpeed(),
            "zoom": self.getZoomSpeed()
        }

    def setPTZSpeeds(self, ptzSpeeds):
        self.panSpeed.setValue(ptzSpeeds["pan"])
        self.tiltSpeed.setValue(ptzSpeeds["tilt"])
        self.zoomSpeed.setValue(ptzSpeeds["zoom"])


    def initSavePresetButton(self):
        def presetSaveToggled(isChecked):
            if(isChecked):
                self.activatePresetSave()
            else:
                self.deactivatePresetSave()
            
        self.presetSaveButton = QPushButton("Change Preset Button\r\nTo Current Position", self)
        self.presetSaveButton.flat = True
        self.presetSaveButton.resize(125,30)
        self.presetSaveButton.move(645,10)
        self.presetSaveButton.setCheckable(True)
        self.presetSaveButton.toggled.connect(presetSaveToggled)
        self.presetSaveButton.setStyleSheet(self.cssStyles["presetSave"]["unselected"])

    def activatePresetSave(self):
        self.presetSaveButton.setStyleSheet(self.cssStyles["presetSave"]["selected"])
        self.presetSaveButton.setText("Click Preset to Save\r\nCurrent Position")

        #disable all the other buttons except for the presets
        self.setDisableStateForButtonGroup(self.cameraButtons, True, self.cssStyles["cameras"]["disabled"])
        self.setDisableStateForButtonGroup(self.ptzButtons, True, self.cssStyles["ptz"]["disabled"])
        self.setDisableStateForButton(self.joystickButton, True, self.cssStyles["joystick"]["disabled"])
        self.setDisableStateForButton(self.panSpeed, True, self.cssStyles["ptzSlider"]["disabled"])
        self.setDisableStateForButton(self.tiltSpeed, True, self.cssStyles["ptzSlider"]["disabled"])
        self.setDisableStateForButton(self.zoomSpeed, True, self.cssStyles["ptzSlider"]["disabled"])

        self.presetSaveButton.repaint()
    
    def deactivatePresetSave(self): 
        self.presetSaveButton.setStyleSheet(self.cssStyles["presetSave"]["unselected"])
        self.presetSaveButton.setText("Change Preset Button\r\nTo Current Position")

        #return all the buttons to their previously enabled states
        self.setDisableStateForButtonGroup(self.cameraButtons, False, self.cssStyles["cameras"]["unselected"])
        self.getSelectedCameraButton().setStyleSheet(self.cssStyles["cameras"]["selected"])

        self.setDisableStateForButtonGroup(self.ptzButtons, False, self.cssStyles["ptz"]["unselected"])

        if(self.joystickButton.isChecked()):
            self.setDisableStateForButton(self.joystickButton, False, self.cssStyles["joystick"]["selected"])
        else:
            self.setDisableStateForButton(self.joystickButton, False, self.cssStyles["joystick"]["unselected"])

        self.setDisableStateForButton(self.panSpeed, False, self.cssStyles["ptzSlider"]["enabled"])
        self.setDisableStateForButton(self.tiltSpeed, False, self.cssStyles["ptzSlider"]["enabled"])
        self.setDisableStateForButton(self.zoomSpeed, False, self.cssStyles["ptzSlider"]["enabled"])

        self.presetSaveButton.repaint()

    def initPresetButtons(self, cameraData):

        def presetClick(button):
            if(self.presetSaveButton.isChecked()):
                if self.debug:
                    print("Saving new position to preset: ", button.action)
                button.setStyleSheet(self.cssStyles["presetSave"]["selected"])
                button.repaint()
                self.actionHandlers["presetSave"](button, self.getSelectedCameraButton().cameraInfo)
                self.presetSaveButton.toggle()
                button.setStyleSheet(self.cssStyles["presets"]["unselected"])
                button.repaint()
            else:
                if self.debug:
                    print("Preset: ", button.action)

                self.activatePreset(button)

                command = {
                    "command": button.action,
                    "extraData": {
                        "speed": self.getPTZSpeeds(),
                        "position": {
                            "pan": button.presetInfo["panPosition"],
                            "tilt": button.presetInfo["tiltPosition"],
                            "zoom": button.presetInfo["zoomPosition"]
                        }
                    },
                    "cameraInfo": self.getSelectedCameraButton().cameraInfo
                }
                self.actionHandlers["sendCommand"](command)

                self.finishPreset(button)

              
        presetTitle = QLabel(self)
        presetTitle.setText("<font style='color: white; font-size: 12pt;'>Presets</font>")
        presetTitle.move(375, 15)
        presetTitle.resize(450,30)

        presetButtons = QButtonGroup(self)
        presetButtons.buttonClicked.connect(presetClick)

        startPresetX = 375
        startPresetY = 50
        maxButtonCount = 12
        numButtons = 0
        for presetButton in cameraData["presets"] :
            newButton = QPushButton(presetButton["text"], self)
            newButton.action = presetButton["command"]
            newButton.presetInfo = presetButton
            newButton.id = cameraData["presets"].index(presetButton)
            newButton.flat = True
            newButton.resize(125,75)
            newButton.move(startPresetX,startPresetY)
            newButton.setStyleSheet(self.cssStyles["presets"]["unselected"])
            newButton.setVisible(False)
            presetButtons.addButton(newButton, newButton.id)

            numButtons += 1
            if((numButtons % 3) == 0) :
                startPresetY += 90
                startPresetX = 375
            else :
                startPresetX += 135

        if(numButtons < maxButtonCount):
            for i in range(numButtons, maxButtonCount) :
                newButton = QPushButton("Not Used", self)
                newButton.flat = True
                newButton.resize(125,75)
                newButton.move(startPresetX,startPresetY)
                newButton.setStyleSheet(self.cssStyles["presets"]["disabled"])
                newButton.setDisabled(True)
                newButton.setVisible(False)
                presetButtons.addButton(newButton)
                numButtons += 1
                if((numButtons % 3) == 0) :
                    startPresetY += 90
                    startPresetX = 375
                else :
                    startPresetX += 135

        return presetButtons
    
    def activatePreset(self, presetId):
        presetButton = self.getPresetButton(presetId)
        if(presetButton != None):
            presetButton.setStyleSheet(self.cssStyles["presets"]["selected"])
            presetButton.repaint()

    def finishPreset(self, presetId):
        presetButton = self.getPresetButton(presetId)
        if(presetButton != None):
            presetButton.setStyleSheet(self.cssStyles["presets"]["unselected"])
            presetButton.repaint()

    def getPresetButton(self, presetId):
        currentCamera = self.getSelectedCameraButton()
        return self.getQPushButtonFromButtonGroup(currentCamera.presetButtonGroup, presetId)
    
    def getPresetButtonId(self, presetButton):
        currentCamera = self.getSelectedCameraButton()
        return currentCamera.presetButtonGroup.id(presetButton)
    
    # def getPresetButtonAction(self, buttonId):
    #     currentCamera = self.getSelectedCameraButton()
    #     return currentCamera.presetButtonGroup.buttons()[buttonId].action
    
    # def getPresetButtonInfo(self, buttonId):
    #     currentCamera = self.getSelectedCameraButton()
    #     return currentCamera.presetButtonGroup.buttons()[buttonId].presetInfo

    def initJoystickControl(self):
        
        joystickActionHandlers = {
            "connected": self.joystickConnected,
            "disconnected": self.joystickDisconnected,
            "action": self.joystickAction
        }

        joystickConfigs = {
            "joystick": self.joystickConfig,
            "speeds": self.uiConfig["speeds"]
        }

        self.joystick = Joystick(joystickConfigs, joystickActionHandlers, self.debug)
        if(self.joystick.detectedJoysticks()):
            self.joystickConnected()
        self.joystick.startConnectionCheck()

    def closeJoystickControl(self):
        self.joystick.stopConnectionCheck()
        self.joystick.stop()

    def joystickConnected(self):
        self.joystickButton.show()
    
    def joystickDisconnected(self):
        self.toggleJoyStickUIButtons(False)
        self.joystickButton.hide()

    def initJoystickUIButtons(self):

        #define a local action, in case any UI actions need to take place
        #before returning to the controller
        def joystickButtonClickAction(checked):
            self.toggleJoyStickUIButtons(checked)

        self.joystickButton = QPushButton("Joystick Disabled", self)
        self.joystickButton.flat = True
        self.joystickButton.resize(125,50)
        self.joystickButton.move(15,415)
        self.joystickButton.setCheckable(True)
        self.joystickButton.toggled.connect(joystickButtonClickAction)
        self.joystickButton.setStyleSheet(self.cssStyles["joystick"]["unselected"])
        self.joystickButton.hide()
    
    def toggleJoyStickUIButtons(self, checked=None):
        isChecked = checked
        if(isChecked == None) :
            isChecked = self.joystickButton.isChecked()

        if(isChecked):
            self.joystickButton.setStyleSheet(self.cssStyles["joystick"]["selected"])
            self.joystickButton.setText("Joystick Enabled")
            self.joystick.stopConnectionCheck()
            self.joystick.start()
        else:
            self.joystickButton.setStyleSheet(self.cssStyles["joystick"]["unselected"])
            self.joystickButton.setText("Joystick Disabled")
            #self.setPTZSpeeds(self.uiConfig["speeds"]["default"])
                        
            if(self.joystick.isUsed):
                self.joystick.stop()
                self.initJoystickControl()
    
    def joystickAction(self, data):
        if("button" in data and data["button"]):
            for command in data["ui"]:
                if(command == "camselect"):
                    self.selectNextCamera()
        
        if("axis" in data):
            #this is movement of the axes
            #self.setPTZSpeeds(data["axisValues"])
            command = {
                "command": data["control"],
                "extraData": {"speed": data["axisValues"]},
                "cameraInfo": self.getSelectedCameraButton().cameraInfo
            }
            self.actionHandlers["sendCommand"](command)
            
        
    #This function is just an abstraction to find the right button
    # we use this function frequently across multiple button groups  
    def getQPushButtonFromButtonGroup(self, buttonGroup, buttonId):
        #if cameraId is not a QPushButton, then
        #search for the the QPushButton object
        #that the Id represents
        if(type(buttonId) == int):
            for theButton in buttonGroup.buttons():
                if(buttonGroup.id(theButton) == buttonId):
                    return theButton
        elif(type(buttonId) == QPushButton):
            return buttonId
        else:
            return None
    
    def setDisableStateForButtonGroup(self, buttonGroup, isDisabled, cssStyle = None):
        for aButton in buttonGroup.buttons():
            self.setDisableStateForButton(aButton, isDisabled, cssStyle)

    def setDisableStateForButton(self, button, isDisabled, cssStyle = None): 
        button.setDisabled(isDisabled)
        if(cssStyle != None):
            button.setStyleSheet(cssStyle)