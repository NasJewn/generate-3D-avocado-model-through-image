#!/usr/bin/env python3
# coding:utf-8
"""
开发平台搭建：
1 python：3.8-3.9
2 dependency(to install,at first)：
       opencv:   pip install opencv-python
       PyQt5： pip install PyQt5

首先运行此文件！！！

"""

from PyQt5.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QApplication,
    QMessageBox,
    QStyle,QAction
)
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import (
    QIcon,
    
)

import sys

from widgets import ModellingWindow, PgmWindow


class MainWindow(QMainWindow):
    """MainWindow"""

    def __init__(self):
        """init"""
        super().__init__()

        self.setWindowTitle("Simulation of Avocado")

        # QStackedWidget can be used to create a user interface similar to the one provided by QTabWidget.
        self.cwin = QStackedWidget()
        self.setCentralWidget(self.cwin)

        self.modelwin = ModellingWindow()
        self.pgmwin = PgmWindow()
        self.cwin.addWidget(self.modelwin)
        self.cwin.addWidget(self.pgmwin)

        #  add other items
        self.initUI()
        self.pgmAct.setEnabled(False)
        
        # slot
        self.modelwin.modeling_ok.connect(self.modelUpdated)
        self.modelwin.originFileChanged.connect(self.onOriginFileChanged)
        
        self.modelwin.updateFile('images/p6.png')
        

    def initUI(self):
        """
        help: https://developpaper.com/examples-of-menu-bar-and-toolbar-in-pyqt5/
        """
        exitAct = QAction(QIcon(self.style().standardPixmap(QStyle.SP_BrowserStop)),
                          'Exit', self, statusTip="Exit...", triggered=self.close)

        self.modelAct = QAction(QIcon(self.style().standardPixmap(QStyle.SP_FileDialogListView)),
                                      'Modelling Window', self, statusTip="show modelling window", triggered=self.showModelWindow)
        self.pgmAct = QAction(QIcon(self.style().standardPixmap(QStyle.SP_FileDialogDetailedView)),
                              'PGM Window', self, statusTip="show PGM window", triggered=self.showPgmWindow)
        aboutAct = QAction('About', self, statusTip="about...", triggered=self.about)

        # menu
        menubar = self.menuBar()
        
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAct)

        viewMenu = menubar.addMenu("&Window")
        viewMenu.addAction(self.modelAct)
        viewMenu.addAction(self.pgmAct)

        helpMenu = menubar.addMenu("&Help")
        helpMenu.addAction(aboutAct)

        # toolbar

        toolbar = self.addToolBar("toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.addAction(self.modelAct)
        toolbar.addAction(self.pgmAct)
        toolbar.addSeparator()
        toolbar.addAction(exitAct)
        
        self.statusBar().showMessage("Ready")
        
        self.setFixedSize(850, 600)

    def showModelWindow(self):
        """"""
        if self.cwin.currentIndex() != 0:
            self.cwin.setCurrentIndex(0)       

    def showPgmWindow(self):
        """"""
        if self.cwin.currentIndex() != 1:
            self.cwin.setCurrentIndex(1)

    def closeEvent(self, event):
        """close confirm."""
        reply = QMessageBox.question(self, 'Confirm', "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        pass

    def about(self):
        """"""
        QMessageBox.information(self, 'About', 'Simulation of Avocado \n version 1.0.0')


    def modelUpdated(self, ok, model):
        """"""
        if ok == 1:
            self.pgmAct.setEnabled(True)
            self.pgmwin.modelReset(model)
            QMessageBox.information(self, 'modeling', 'modeling successed')
            self.cwin.setCurrentWidget(self.pgmwin)

        else:
            self.pgmAct.setEnabled(False)
            
            
    def onOriginFileChanged(self, file):
        self.setWindowTitle(f"Simulation of Avocado - {file}")


# ========== run from here, startpoint ============
if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MainWindow()
    w.showNormal()

    sys.exit(app.exec())
