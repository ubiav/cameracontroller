#!/usr/bin/python

import sys
from PyQt5.QtWidgets import QApplication
from controller.Controller import Controller

def main():

    app = QApplication(sys.argv)
    
    #instantiate a new controller object
    #this will kick it all off and get the system
    #up and running
    myController = Controller()
    myController.start()

    #when controller exits, clean everything up
    sys.exit(app.exec())

if __name__ == '__main__':
    main()