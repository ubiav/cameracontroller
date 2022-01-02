import socket, time, binascii

from controller.ViscaOverIPMessage import ViscaOverIPMessage

class ViscaOverIPService:
    
    SEQNUM = 0

    def __init__(self, config, debug=False):
        super().__init__()
        self.config = config
        self.debug = debug
        self.resetSeqNum()
        self.initUDPServer()
        
    def resetSeqNum(self):
        self.SEQNUM = 1
    
    def initUDPServer(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(self.config["commandTimeout"])
        self.socket.bind((self.config["ip"], self.config["port"]))
    
    def closeUDPServer(self):
        self.socket.close()

    def sendUDPMessage(self, commands):
        #format of the data should be a single object
        # i.e. 
        #   commands = { "command": command_name, "extraData": extra_data }
        #   OR
        #   commands = { "command":"ACK", "extraData": { "pan": [0,0,0,0]} }
        #
        #OR an array of these objects
        # i.e.
        #   commands = [
        #       { "command":"PanRight", "extraData": { "pan": [0,0,0,0]} },
        #       { "command":"ZoomTele", "extraData": { "zoom": [0,0,0,0]} }
        #   ]

        #check for valid Commands and if they aren't there, then
        #don't do anything and just return

        if(type(commands) != list and type(commands) == dict):
            commands = [commands]
        elif(type(commands) != list):
            return None

        #loop through each command and send them to the camera
        #an array of commands allows for pre-programmed sequences
        for commandObject in commands:
            #require the cameraInfo and the command itself
            if("command" in commandObject and "cameraInfo" in commandObject):
                # command = commandObject["command"]
                # cameraInfo = commandObject["cameraInfo"]

                if("extraData" not in commandObject):
                    commandObject["extraData"] = {}

                ViscaMessage = ViscaOverIPMessage(self.debug)
                ViscaMessage.setPayloadByCommandName(commandObject["command"], commandObject["extraData"])
                ViscaMessage.setSequenceNumber(self.SEQNUM)
                udpMessage = ViscaMessage.getFullMessageAsByteArray()

                if self.debug:
                    print(commandObject["cameraInfo"]["ip"], commandObject["cameraInfo"]["port"], commandObject["command"], binascii.hexlify(udpMessage))

                self.socket.sendto(udpMessage, (commandObject["cameraInfo"]["ip"], commandObject["cameraInfo"]["port"]))
                
                #keep looping for a final state
                #some states are informational only
                validMessage = None
                while(validMessage == None):
                    response = self.getUDPResponse()
                    validMessage = ViscaMessage.isValidResponse(response)
                
                if(validMessage):
                    if(self.debug):
                        print("Valid response verified")

                    ##if there is a Zoom component to this Preset, then send the Zoom Command as well
                    if(commandObject["command"] == "PresetPanTilt" and len(commandObject["extraData"]['position']['zoom']) > 0):
                        time.sleep(0.1)
                        self.SEQNUM += 1
                        command = {
                            "command": "PresetZoom",
                            "extraData": commandObject["extraData"],
                            "cameraInfo": commandObject["cameraInfo"]
                        }
                        return self.sendUDPMessage(command)

                    if(commandObject["command"] == "Home"):
                        time.sleep(0.1)
                        self.SEQNUM += 1
                        command = {
                            "command": "PresetZoom",
                            "extraData": [[], [], [0x00, 0x00, 0x00, 0x00]],
                            "cameraInfo": commandObject["cameraInfo"]
                        }
                        return self.sendUDPMessage(command)
                
                    if(commandObject["command"] == "SEQNO_RESET"):
                        self.resetSeqNum()
                    else:
                        print("Incrementing SEQNUM", self.SEQNUM)
                        self.SEQNUM += 1
                    
                    if self.debug:
                        print("Command(s) Successful!")
                    
                    return True
                elif(validMessage == False and validMessage != None):
                    if(commandObject["command"] != "SEQNO_RESET"):
                        if self.debug:
                            print("Command(s) failed, resetting sequence number")
                        
                        self.resetSeqNum()
                        
                        #command completely failed, so reset the sequence Number
                        command = {
                            "command": "SEQNO_RESET",
                            "cameraInfo": commandObject["cameraInfo"]
                        }
                        self.sendUDPMessage(command)
                        return False
                    if self.debug:
                        print("Command(s) failed")            
                    return None
            else:
                if self.debug:
                    print("Command(s) failed")
                return None


    def getUDPResponse(self):
        try:
            (data, remoteAddress) = self.socket.recvfrom(1024)
            print("after receive")
        except socket.timeout:
            return None                
        else:
            if self.debug:
                print("Received: ", binascii.hexlify(data), ' From:', remoteAddress)

            response = ViscaOverIPMessage(self.debug)
            response.loadFromReceivedPacket(data)
            
            return response
    
    #     #         if(messageType == "VISCA_COMMAND"):
    #     #             #look for a VISCA reply
    #     #             VISCA_ACK = self.getMessagePacketFromStringName("VISCA_ACK")
    #     #             VISCA_ACK2 = self.getMessagePacketFromStringName("VISCA_ACK2")
    #     #             VISCA_COMPLETE = self.getMessagePacketFromStringName("VISCA_COMPLETE")
    #     #             VISCA_COMPLETE2 = self.getMessagePacketFromStringName("VISCA_COMPLETE2")
    #     #             VISCA_CANTEXECUTE = self.getMessagePacketFromStringName("VISCA_CANTEXECUTE")
                    
    #     #             if(data == VISCA_ACK or data == VISCA_ACK2):
    #     #                 print("ACK VISCA REPLY: ", binascii.hexlify(VISCA_ACK))
                        
                    
    #     #             if(data == VISCA_COMPLETE or data == VISCA_COMPLETE2):
    #     #                 #print("COMPLETE VISCA REPLY: ", binascii.hexlify(VISCA_COMPLETE))
    #     #                 commandComplete = True
                    
    #     #             if(data == VISCA_CANTEXECUTE):
    #     #                 #print("CANT EXECUTE VISCA REPLY: ", binascii.hexlify(VISCA_CANTEXECUTE))
    #     #                 commandFailed = True

    #     #         elif(messageType == "CONTROL_COMMAND"):
    #     #             #look for a CONTROL REPLY
    #     #             if(data == self.getMessagePacketFromStringName("CONTROL_ACK")):
    #     #                 commandComplete = True
        
    #     # if(commandFailed):
    #     #     return False
    #     # else: 
    #     #     return commandComplete

