import pygame, threading, time

class Joystick(threading.Thread):
    maxPanSpeed = 0x18
    maxTiltSpeed = 0x17
    connectionTimer = None
    isRunning = False
    isUsed = False
    keepCheckingForJoystick = False

    def __init__(self, configs, actionHandlers, debug = False):

        super().__init__()
        self.joystickConfig = configs["joystick"]
        self.speedConfig = configs["speeds"]
        self.actionHandlers = actionHandlers
        self.debug = debug

        # self.axesAction = axesAction
        # self.buttonAction = buttonAction
        # self.hatAction = hatAction
        # self.ballAction = ballAction

        pygame.init()
        pygame.joystick.init()
    
    def close(self):
        while self.isRunning:
            self.stop()
            pygame.joystick.quit()
            pygame.quit()
    
    def startConnectionCheck(self, timeToWait = 1):

        def checkIfJoystickConnected():
            while(self.keepCheckingForJoystick):
                for eventAction in pygame.event.get():
                    if(eventAction.type == pygame.JOYDEVICEADDED):
                        if self.debug:
                            print("Found a joystick connect event")
                        self.actionHandlers["connected"]()
                    elif(eventAction.type == pygame.JOYDEVICEREMOVED):
                        if self.debug:
                            print("Found a joystick disconnect event")
                        self.actionHandlers["disconnected"]()
                
                time.sleep(timeToWait)

        self.keepCheckingForJoystick = True
        self.connectionTimer = threading.Timer(timeToWait, checkIfJoystickConnected)
        self.connectionTimer.start()
    
    def stopConnectionCheck(self):
        self.keepCheckingForJoystick = False
    
    def detectedJoysticks(self):
        return (self.getJoystickCount() > 0)
    
    def getJoystickCount(self):
        return pygame.joystick.get_count()

    def run(self):

        def absAxisValues(axisValues):
            newAxisValues = {}
            for controlName in axisValues:
                newAxisValues[controlName] = abs(axisValues[controlName])
            return newAxisValues

        # This is how fast we'll check the queue
        # the lower the number the more updates it will make
        # but also the more messages sent to the camera
        #
        # NOTE: the way that the controller is coded, this isn't
        # strictly necessary... The flow of the program will wait
        # for response from the cameras before checking the joystick commands again
        # and we'll only take the latest command.
        # This means that it is sort of self-regulating... only
        # checking the joysticks when the cameras can handle more input
        # but it's here just in case it needs to be adjusted.
        # for now, it is at a very low value
        TIME_DELAY = 0.01

        #we only support one joystick
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        self.isUsed = True
        self.isRunning = True

        axisValues = {
            "pan": 0,
            "tilt": 0,
            "zoom": 0
        }

        commands = {
            "movement": [],
            "ui": []
        }
        
        while (self.isRunning):
            #we want to "debounce" the joystick.
            #I don't want to send a command on every action received
            # or I could overload the camera with so many commands.
            # instead, I'll send the most recent joystick event since the last
            # time we checked.  We can adjust the TIME_DELAY constant
            # to adjust how responsive it feels

            #collect all the actions that we've received
            #since the last time you've checked
            #but only keep one action for each check
            tempEventList = {}
            for eventAction in pygame.event.get():
                tempEventList[eventAction.type] = eventAction

            #now recreate the event array
            newEventList = []
            for eventType in tempEventList:
                newEventList.append(tempEventList[eventType])
            
            #now go through all the latest actions
            for eventAction in newEventList:
                # if self.debug:
                #     print("Joystick Event:", eventAction)

                if eventAction.type == pygame.JOYAXISMOTION:
                    hasChanged, axisControlName, axisValues = self.convertAxisRawMovement(eventAction.axis, eventAction.value, axisValues)
                    if(hasChanged):
                        commands["movement"] = self.getAxisCommand(axisValues, axisControlName)
                        self.actionHandlers["action"]({"axis": True, "axisValues": absAxisValues(axisValues), "control": commands["movement"]})
                
                if eventAction.type == pygame.JOYBUTTONDOWN:
                    commands["ui"] = self.getButtonCommands(eventAction.button, True, commands["ui"])
                    self.actionHandlers["action"]({"button": True, "ui": commands["ui"]})
                
                if eventAction.type == pygame.JOYBUTTONUP:
                    commands["ui"] = self.getButtonCommands(eventAction.button, False, commands["ui"])
                    self.actionHandlers["action"]({"button": True, "ui": commands["ui"]})
                
                if eventAction.type == pygame.JOYDEVICEREMOVED:
                    #this will make it look, at least temporarily,
                    #like all the joysticks have been removed
                    #if there is still one connected, though,
                    #the connectionTimer will quickly pick it up
                    if self.debug:
                        print("Found a joystick disconnect event")
                    self.actionHandlers["disconnected"]()
                    
            
            #give a quick break in the thread loop
            time.sleep(TIME_DELAY)
    
    def convertAxisRawMovement(self, axis, value, axisValues):
        #check to make sure we have a configuration for the axis
        sAxis = str(axis)
        if(sAxis in dict.keys(self.joystickConfig["axes"])):
            axisFromConfig = self.joystickConfig["axes"]
            axisControlName = axisFromConfig[sAxis]["control"]
            maxValue = self.speedConfig["max"][axisControlName]
            axisVector = round(value * maxValue)
            axisDirection = 1 if (axisVector > 0) else -1
            axisValue = abs(axisVector)
            
            #ensure that any error in math doesn't cause issues
            if(axisValue > 0 and axisValue > maxValue):
                axisValue = maxValue
                axisVector = axisValue * axisDirection
            
            if(axisVector != axisValues[axisControlName]):
                axisValues[axisControlName] = axisVector
                return True, axisControlName, axisValues
            else:
                return False, axisControlName, axisValues
        
        return False, None, axisValues

    def getActiveAxes(self, axisValues):
        activeAxis = {
            "pan": False,
            "tilt": False,
            "zoom": False
        }

        for axisControlName in axisValues:
            if(axisValues[axisControlName] != 0):
                activeAxis[axisControlName] = True
        
        return activeAxis
    
    def getAxisCommand(self, axisValues, axisControlName):
        STOP = 0

        PT_MOVEMENTS = {
            "pan": {
                -1: 4,
                0: 0,
                1: 8
            },
            "tilt": {
                -1: 1,
                0: 0,
                1: 2
            }
        }

        ZOOM_TELE = 1
        ZOOM_WIDE = 2       
        
        panTiltCommands = {
            0: "PanTiltStop",
            1: "TiltUp",
            2: "TiltDown",
            4: "PanLeft",
            5: "PanTiltUpLeft",
            6: "PanTiltDownLeft",
            8: "PanRight",
            9: "PanTiltUpRight",
            10: "PanTiltDownRight"
        }

        zoomCommands = {
            0: "ZoomStop",
            1: "ZoomTele",
            2: "ZoomWide"
        }

        ptCode = 0
        activeCommands = ""
        
        if(axisControlName == "pan" or axisControlName == "tilt"):
            ptIndex = 1 if(axisValues[axisControlName] > 0) else (-1 if(axisValues[axisControlName] < 0) else 0)
            ptCode += PT_MOVEMENTS[axisControlName][ptIndex]
            activeCommands = panTiltCommands[ptCode]

        if(axisControlName == "zoom"):
            if(axisValues["zoom"] > 0):
                activeCommands = zoomCommands[ZOOM_TELE]
            elif(axisValues["zoom"] < 0):
                activeCommands = zoomCommands[ZOOM_WIDE]
            else:
                activeCommands = zoomCommands[STOP]

        return activeCommands
    
    def getButtonCommands(self, buttonId, isPressed, uiCommands):
        
        sButtonId = str(buttonId)

        if(sButtonId in dict.keys(self.joystickConfig["buttons"])):
            if(not isPressed):
                #look for the item in the array.
                newUICommands = []
                for command in uiCommands:
                    if command != self.joystickConfig["buttons"][sButtonId]["control"]:
                        newUICommands.append(command)
                uiCommands = newUICommands
            else:
                alreadyInList = False
                for command in uiCommands:
                    if command == self.joystickConfig["buttons"][sButtonId]["control"]:
                        alreadyInList = True
                
                if(not alreadyInList):
                    uiCommands.append(self.joystickConfig["buttons"][sButtonId]["control"])
        
        return uiCommands

    def stop(self):
        self.isRunning = False
        