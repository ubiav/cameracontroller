import binascii

class ViscaOverIPMessage:

    BYTE_POSITIONS = {
        "CAM": 0,
        "ZOOM_SPEED": 4,
        "PAN_SPEED": 4,
        "TILT_SPEED": 5,
        "PAN_POSITION": [6,4],
        "TILT_POSITION": [10, 4],
        "ZOOM_POSITION": [4, 4],
        "TYPE": [0, 2],
        "LENGTH": [2, 2],
        "SEQUENCE_NUMBER": [4, 4],
        "PAYLOAD_START": 8
    }

    PAYLOAD_TYPES = {
        "VISCA_COMMAND": bytearray([0x01, 0x00]),
        "VISCA_INQUIRY": bytearray([0x01, 0x10]),
        "VISCA_REPLY": bytearray([0x01, 0x11]),
        "VISCA_DEVICESETTING": bytearray([0x01, 0x20]),
        "CONTROL_COMMAND": bytearray([0x02, 0x00]),
        "CONTROL_REPLY": bytearray([0x02, 0x01])
    }

    PAYLOAD_TEMPLATES = {
            "VISCA_COMMAND": {
                "PowerOn": bytearray([0x80, 0x01, 0x04, 0x00, 0x02, 0xFF]),
                "PowerOff": bytearray([0x80, 0x01, 0x04, 0x00, 0x03, 0xFF]),
                "HOME": bytearray([0x80, 0x01, 0x06, 0x04, 0xFF]),
                "ZoomStop": bytearray([0x80, 0x01, 0x04, 0x07, 0x00, 0xFF]),
                "ZoomTele": bytearray([0x80, 0x01, 0x04, 0x07, 0x02, 0xFF]),
                "ZoomWide": bytearray([0x80, 0x01, 0x04, 0x07, 0x03, 0xFF]),
                "TiltUp": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x03, 0x01, 0xFF]),
                "TiltDown": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x03, 0x02, 0xFF]),
                "PanTiltUpLeft": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x01, 0x01, 0xFF]),
                "PanTiltUpRight": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x02, 0x01, 0xFF]),
                "PanTiltDownLeft": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x01, 0x02, 0xFF]),
                "PanTiltDownRight": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x02, 0x02, 0xFF]),
                "PanTiltStop": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x03, 0x03, 0xFF]),
                "PanLeft": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x01, 0x03, 0xFF]),
                "PanRight": bytearray([0x80, 0x01, 0x06, 0x01, 0x18, 0x18, 0x02, 0x03, 0xFF]),
                "PresetPanTilt": bytearray([0x80, 0x01 ,0x06 ,0x02 ,0x18 ,0x18 ,0x00 ,0x00 ,0x00 ,0x00 ,0x00 ,0x00 ,0x00 ,0x00 ,0xFF]),
                "PresetZoom": bytearray([0x80, 0x01 ,0x04 ,0x47 ,0x00 ,0x00 ,0x00 ,0x00 ,0xFF])
            },
            "VISCA_INQUIRY": {
                "INQPT": bytearray([0x80, 0x09, 0x06, 0x12, 0xFF]),
                "INQZOOM": bytearray([0x80, 0x09, 0x04, 0x47, 0xFF])
            },
            "VISCA_REPLY": {
                "VISCA_ACK": bytearray([0x90, 0x41, 0xff]),
                "VISCA_ACK2": bytearray([0x90, 0x42, 0xff]),
                "VISCA_COMPLETE": bytearray([0x90, 0x51, 0xff]),
                "VISCA_COMPLETE2": bytearray([0x90, 0x52, 0xff]),
                "VISCA_CANTEXECUTE": bytearray([0x90, 0x62, 0x41, 0xFF]),
                "VISCA_INQRESPONSE": bytearray([0x90, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF])
            },
            "CONTROL_COMMAND": {
                "SEQNO_RESET": bytearray([0x01])
            },
            "CONTROL_REPLY": {
                "CONTROL_ACK": bytearray([0x01])
            }
        }

    def __init__(self, debugFlag):
        super().__init__()
        self.initType()
        self.initSequenceNumber()
        self.initPayload()
        self.debug = debugFlag
        self.commandName = ""

    def initType(self):
        self.messageType = bytearray()
    
    def setType(self, messageTypeByteArray):
        self.initType()
        if(type(messageTypeByteArray) is bytearray):
            self.messageType = messageTypeByteArray
    
    def setTypeByName(self, messageTypeName):
        self.initType()
        if messageTypeName in self.PAYLOAD_TYPES:
            self.setType(self.PAYLOAD_TYPES[messageTypeName])
    
    def setTypeByCommandName(self, commandName):
        self.commandName = commandName
        if(type(commandName) is str):
            for typeName in self.PAYLOAD_TYPES:
                if typeName in self.PAYLOAD_TEMPLATES:
                    for cmdName in self.PAYLOAD_TEMPLATES[typeName]:
                        if commandName == cmdName:
                            self.setType(self.PAYLOAD_TYPES[typeName])        
    
    def getType(self):
        return self.messageType
    
    def getTypeName(self):
        for typeName in self.PAYLOAD_TYPES:
            #print(self.PAYLOAD_TYPES[typeName], "=", self.getType())
            if(self.PAYLOAD_TYPES[typeName] == self.getType()):
                return typeName
        
        return None
    
    def initSequenceNumber(self):
        self.setSequenceNumber(0)           
    
    def setSequenceNumber(self, sequenceNumber):
        if(type(sequenceNumber) is int):
            self.messageSequenceNumber = sequenceNumber
        
    def setSequenceNumberFromByteArray(self, seqNumByteArray):
        if(type(seqNumByteArray) is bytearray):
            firstNum = seqNumByteArray[0] * 16
            self.setSequenceNumber(firstNum + seqNumByteArray[1])
    
    def getSequenceNumber(self):
        return self.messageSequenceNumber
    
    def getSequenceNumberAsByteArray(self):
        return self.convertIntToBytes(self.getSequenceNumber(), 4)

    def initPayload(self):
        self.setPayload(bytearray())
    
    def setPayload(self, payloadByteArray):
        if(type(payloadByteArray) is bytearray):
            self.messagePayload = payloadByteArray
    
    def setPayloadByCommandName(self, commandName, extraData = {}):
        self.commandName = commandName
        if(len(self.getType()) <= 0):
            print("Setting new Type: ", commandName)
            #set the payload type based on the commandName
            self.setTypeByCommandName(commandName)
            print("Set new Type: ", self.getTypeName())

        #the payload Type has already been set
        if commandName in (self.PAYLOAD_TEMPLATES[self.getTypeName()]):
            self.setPayload(self.getPayloadByCommandName(commandName))
        
        self.overridePayload(commandName, extraData)
    
    def getPayload(self):
        return self.messagePayload
    
    def getPayloadByCommandName(self, commandName):
        self.commandName = commandName
        #the payload Type has already been set
        if commandName in (self.PAYLOAD_TEMPLATES[self.getTypeName()]):
            return self.PAYLOAD_TEMPLATES[self.getTypeName()][commandName]
        else:
            return bytearray()
    
    def overridePayload(self, commandName, extraData = {}):
        self.commandName = commandName

        messageType = self.getTypeName()
        messageCommand = self.getPayload()
    

        if messageType == "VISCA_COMMAND" or messageType == "VISCA_INQUIRY":
            if(messageCommand[self.BYTE_POSITIONS["CAM"]] != 0x81):
                messageCommand[self.BYTE_POSITIONS["CAM"]] = 0x81

            if commandName == "ZoomTele":
                messageCommand[self.BYTE_POSITIONS["ZOOM_SPEED"]] = 0x20 + extraData["speed"]["zoom"]
                
            if commandName == "ZoomWide":
                messageCommand[self.BYTE_POSITIONS["ZOOM_SPEED"]] = 0x30 + extraData["speed"]["zoom"]
            
            if commandName == "TiltUp" or \
                    commandName == "TiltDown" or \
                    commandName == "PanLeft" or \
                    commandName == "PanRight" or \
                    commandName == "PanTiltUpRight" or \
                    commandName == "PanTiltUpLeft" or \
                    commandName == "PanTiltDownRight" or \
                    commandName == "PanTiltDownLeft":
                messageCommand[self.BYTE_POSITIONS["PAN_SPEED"]] = extraData["speed"]["pan"]
                messageCommand[self.BYTE_POSITIONS["TILT_SPEED"]] = extraData["speed"]["tilt"]
            
            if commandName == "PresetPanTilt" and \
                    len(extraData['position']["pan"]) > 0 and \
                    len(extraData['position']["tilt"]) > 0 :
                
                panPosition = self.BYTE_POSITIONS["PAN_POSITION"]
                messageCommand[panPosition[0]:panPosition[0]+panPosition[1]] = extraData['position']["pan"]
                
                tiltPosition = self.BYTE_POSITIONS["TILT_POSITION"]
                messageCommand[tiltPosition[0]:tiltPosition[0]+tiltPosition[1]] = extraData['position']["tilt"]
            
            if commandName == "PresetZoom" and len(extraData['position']["zoom"]) > 0 :
                zoomPosition = self.BYTE_POSITIONS["ZOOM_POSITION"]
                messageCommand[zoomPosition[0]:zoomPosition[0]+zoomPosition[1]] = extraData['position']["zoom"]

    def getLength(self):
        return len(self.getPayload())
    
    def getLengthInBytes(self):
        return self.convertIntToBytes(self.getLength(), 2)

    def getFullMessageAsByteArray(self):
        if(len(self.messageType) == 0) or (len(self.getPayload()) == 0):
            return bytearray()
        
        if(self.getTypeName() != "CONTROL_REPLY"):
            return bytearray(self.getType() + self.getLengthInBytes() +  self.getSequenceNumberAsByteArray() + self.getPayload())
        else:
            return bytearray(self.getType() + self.getLengthInBytes() +  bytearray(self.convertIntToBytes(0x00, 4)) + self.getPayload())

    def getFullMessageAsByteArrayFromCommandName(self, commandName):
        newMessage = ViscaOverIPMessage(self.debug)
        newMessage.setPayloadByCommandName(commandName)
        return newMessage.getFullMessageAsByteArray()
    
    def loadFromReceivedPacket(self, messageFromNetwork):
        byteArrayMessage = bytearray(messageFromNetwork)

        typePosition = self.BYTE_POSITIONS["TYPE"]
        self.setType(byteArrayMessage[typePosition[0]:typePosition[0]+typePosition[1]])

        seqPosition = self.BYTE_POSITIONS["SEQUENCE_NUMBER"]
        self.setSequenceNumberFromByteArray(byteArrayMessage[seqPosition[0]:seqPosition[0]+seqPosition[1]])

        lengthPosition = self.BYTE_POSITIONS["LENGTH"]
        payloadLengthByteArray = byteArrayMessage[lengthPosition[0]:lengthPosition[0]+lengthPosition[1]]
        payloadLength = (payloadLengthByteArray[0] * 16) + payloadLengthByteArray[1]

        payloadStart = self.BYTE_POSITIONS["PAYLOAD_START"]
        newPayload = byteArrayMessage[payloadStart:payloadStart+payloadLength]

        self.setPayload(newPayload)
         
    def isValidResponse(self, response):
        if(response == None):
            if(self.debug):
                print("No response received to verify.")
            return False
        elif(self.getTypeName() == "VISCA_COMMAND"):
            responseArray = response.getFullMessageAsByteArray()
            if(responseArray == self.getFullMessageAsByteArrayFromCommandName("VISCA_ACK")) or \
                (responseArray == self.getFullMessageAsByteArrayFromCommandName("VISCA_ACK2")):
                if(self.debug):
                    print("Received an ACK Message")
                return None
            elif (responseArray == self.getFullMessageAsByteArrayFromCommandName("VISCA_COMPLETE")) or \
                (responseArray == self.getFullMessageAsByteArrayFromCommandName("VISCA_COMPLETE2")):
                if(self.debug):
                    print("Received a COMMAND COMPLETE Message")
                return True
            elif (responseArray == self.getFullMessageAsByteArrayFromCommandName("VISCA_CANTEXECUTE")):
                if(self.debug):
                    print("Received an CANTEXECUTE Message")
                return False
        elif self.getTypeName() == "VISCA_INQUIRY":
            if(response.getFullMessageAsByteArray()[0:2] == self.getFullMessageAsByteArrayFromCommandName("VISCA_INQRESPONSE")[0:2]):
                thisPayload = response.getPayload()
                if(self.commandName == "INQPT"):
                    #this is INQ response for PanTilt
                    panPosition = thisPayload[2:4]
                    tiltPosition = thisPayload[6:4]
                    if(self.debug):
                        print("Received Pan Tilt Inquiry Response.  Pan Position [", binascii.hexlify(panPosition),"]\tTilt Position [", binascii.hexlify(tiltPosition), "]")
                    return True
                elif self.commandName == "INQZOOM":
                    #this is INQ response for ZOOM
                    zoomPosition = thisPayload[2:4]
                    if(self.debug):
                        print("Received Pan Tilt Inquiry Response.  Pan Position [", binascii.hexlify(zoomPosition),"]")
                    return True

        elif self.getTypeName() == "CONTROL_COMMAND":
            if(response.getFullMessageAsByteArray() == self.getFullMessageAsByteArrayFromCommandName("CONTROL_ACK")):
                if(self.debug):
                    print("Received an CONTROLACK Message")
                return True
                
    def convertIntToBytes(self, theInteger, length, endian='big') :
        return theInteger.to_bytes(length, byteorder=endian)
            



