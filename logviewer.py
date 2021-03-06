#!/usr/bin/python3
# -*- coding: utf-8 -*-


# Pour les problèmes de compatibilité Python 2 - 3 voir
# http://stackoverflow.com/questions/8307985/incompatibility-between-python-3-2-and-qt

# http://joplaete.wordpress.com/2010/07/21/threading-with-pyqt4/

# TODO: si l'utilisateur s'scrollait en bas pdt le chargement, il reste scrollé en bas qd la suite du texte se charge

import sys
from PyQt4 import QtCore, QtGui
from time import time, sleep

from loganalyser import *
from ui import Ui_MainWindow

class ThreadedLogAnalyser(QtCore.QThread):
    def __init__(self, parent, logAnalalyser):
        QtCore.QThread.__init__(self, parent)
        self.logAnalyser = logAnalyser
        self.parent = parent
        
    def run(self):
        locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
        prevTime = 0
        cumulatedLogs = self.logAnalyser.analyseStep()
        while self.logAnalyser.termination > 0:
            logs = self.logAnalyser.analyseStep()
            self.usleep(200)
            for i in range(len(cumulatedLogs)):
                cumulatedLogs[i] += logs[i]
            if time() - prevTime > 0.5:
                prevTime = time()
                self.emit(QtCore.SIGNAL("appendLogs"), cumulatedLogs)
                cumulatedLogs = self.logAnalyser.analyseStep()
        self.emit(QtCore.SIGNAL("appendLogs"), cumulatedLogs)
        print("File loaded")

class MyForm(QtGui.QMainWindow):
    def __init__(self, logAnalyser, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, len(logAnalyser.files))
        self.logAnalyser = logAnalyser
        self.threadLogAnalyser =  ThreadedLogAnalyser(self, self.logAnalyser)
        self.connect(self.threadLogAnalyser, QtCore.SIGNAL("appendLogs"), self.ui.appendLogs)

    
        
    def main(self):
        self.threadLogAnalyser.start()
        

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.stderr.write("""Logviewer needs one or more arguments : 
        the filenames of the logs you want to read simulataneously\n""")
        sys.exit(-1)
    logs = []
    for arg in sys.argv[1:]:
        logs.append(LogFile(arg, lineParser))
    logAnalyser = LogAnalyser(logs)
    
    
    app   = QtGui.QApplication(sys.argv)
    myapp = MyForm(logAnalyser)
    
    myapp.show()
    myapp.main()
    
    sys.exit(app.exec_())
