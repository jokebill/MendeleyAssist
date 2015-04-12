#!/usr/bin/python
import sys
from PyQt4 import QtGui, QtCore
import sqlite3 as sql
import kernel as ma
import logging
    
class MyWin(QtGui.QWidget):

    def __init__(self):
        super(MyWin,self).__init__()
        self.dbfile=""
        self.refpath=""
        self.progfile=""
        self.initUI()

    def initUI(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle(u'Test window')
        self.resize(700,300)
        self.bt1 = QtGui.QPushButton(u'Select the database file')
        self.bt2 = QtGui.QPushButton(u'Select the reference folder')
        self.bt3 = QtGui.QPushButton(u'Select the program file')
        self.bt4 = QtGui.QPushButton(u'Save and fix the paths')
        self.ed1 = QtGui.QTextEdit()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.ed1)
        layout.addWidget(self.bt1)
        layout.addWidget(self.bt2)
        layout.addWidget(self.bt3)
        layout.addWidget(self.bt4)
        self.setLayout(layout)
        self.bt0.clicked.connect(self.selass)
        self.bt1.clicked.connect(self.seldb)
        self.bt2.clicked.connect(self.selref)
        self.bt3.clicked.connect(self.selprog)
        self.bt4.clicked.connect(self.commit)        

    def dispinfo(self):
        self.ed1.setText('''
Database :\t{0}
Ref Folder :\t{1}
Program :\t{2}'''.format(self.dbfile,self.refpath,self.progfile))
                         
    def seldb(self):
        self.dbfile = str(QtGui.QFileDialog.getOpenFileName(
            self,self.tr("Select the Mendeley database File"),
            self.tr(""),self.tr("Database (*.sqlite)")))
        self.dispinfo()

    def selref(self):
        self.refpath = str(QtGui.QFileDialog.getExistingDirectory(
            self,self.tr("Select the Mendeley reference folder"),
            options = QtGui.QFileDialog.ShowDirsOnly))
        self.dispinfo()

    def selprog(self):
        self.progfile = str(QtGui.QFileDialog.getOpenFileName(
            self,self.tr("Select the Mendeley Desktop Executive File"),
            self.tr(""), self.tr("Executive (*.exe *.* *)")))
        self.dispinfo()

    def commit(self):
        if self.asspath == "":
            self.selass()
        if self.dbfile == "":
            self.seldb()
        if self.refpath == "":
            self.selref()
        if self.progfile == "":
            self.selprog()
        self.close()

def setpath():
    app = QtGui.QApplication(sys.argv)
    mainwin = MyWin()
    mainwin.show()
    app.exec_()
    log=logging.getLogger('setpathwin')
    r={'dbfile':mainwin.dbfile,
            'refpath':mainwin.refpath,
            'progfile':mainwin.progfile}
    log.debug('''-----args input in mainwin---
    {0}'''.format(ma.dictdisp(r)))
    return r

def main():
    from opts import getopts
    import os
    projdir=os.path.sep.join(os.getcwd().split(os.path.sep)[:-1])
    logfile=os.path.join(projdir,'logs','MendeleyAssist.log')
    opts=getopts(logfile)
    ma.fixpath(setpath, opts['reset'])

if __name__ == '__main__':
    main()
