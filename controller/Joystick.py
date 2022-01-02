import enum
import pygame, threading, time, math

class Joystick(threading.Thread):
    maxPanSpeed = 0x18
    maxTiltSpeed = 0x17

    def __init__(self, joyConfig, debug, axesAction = None, buttonAction = None, hatAction = None, ballAction = None):

        super().__init__()
        self.quit = False
        self.joystickConfig = joyConfig
        self.debug = debug

        self.axesAction = axesAction
        self.buttonAction = buttonAction
        self.hatAction = hatAction
        self.ballAction = ballAction

        pygame.init()
        pygame.joystick.init()
    
    def close(self):
        while self.is_alive():
            self.quit = True
            pygame.joystick.quit()
            pygame.quit()
    
    def detectedJoysticks(self):
        return (self.getJoystickCount() > 0)
    
    def getJoystickCount(self):
        return pygame.joystick.get_count()

    def run(self):

        #we only support one joystick
        joystick = pygame.joystick.Joystick(0)
        joystick.init()        
        
        while (not self.quit) and (self.detectedJoysticks()):
            for eventAction in pygame.event.get():
                if eventAction.type == pygame.JOYAXISMOTION:
                    if self.axesAction != None:
                        self.axesAction(eventAction)
                
                if eventAction.type == pygame.JOYBUTTONDOWN:
                    if self.buttonAction != None:
                        self.buttonAction(eventAction)
            
            #give a quick break in the thread loop
            time.sleep(0.01)