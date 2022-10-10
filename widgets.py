#!/usr/bin/env python3
# coding:utf-8
"""


opencv:
    https://www.cnblogs.com/-wenli/p/11951946.html
    pip install opencv-python

"""

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QLineEdit, QRadioButton, QGridLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal

import cv2 as cv
from algos import edge, binary, scale_img, model3D


class ImageWindow(QLabel):
    """"""

    def __init__(self, parent=None, img_file=None, gray_if=False, size=(250, 400)):
        """Constructor"""

        super().__init__(parent=parent)
        self.cvimg = None

        if img_file is not None:
            self.setFile(img_file, gray_if)

        self.setFixedSize(size[0], size[1])

    def display_img(self, qtimg):
        """"""
        pix = QPixmap.fromImage(qtimg)
        pix = pix.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.setPixmap(pix)

        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def read_img(self, img_file):
        """"""
        cvimg = cv.imread(img_file, cv.IMREAD_UNCHANGED)

        return cvimg

    def cvimg2Qt(self, cvimg, gray_if=True):
        """
        ref:https://stackoverflow.com/questions/52869400/how-to-show-image-to-pyqt-with-opencv
        """
        qtimg = None

        if gray_if:
            cvimg = cv.cvtColor(cvimg, cv.COLOR_GRAY2RGB)

        qtimg = QImage(cvimg.data, cvimg.shape[1], cvimg.shape[0], cvimg.strides[0], QImage.Format_RGB888)

        return qtimg

    def setFile(self, img_file, gray_if=True):
        """"""
        cvimg = self.read_img(img_file)

        self.cvimg = scale_img(cvimg, self.width(), self.height())

        pix = QPixmap(img_file)
        pix = pix.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.setPixmap(pix)

        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def setImage(self, qtimg):
        """"""
        self.display_img(qtimg)

    def setPgm(self, pgm_data):
        """"""
        qtimg = self.cvimg2Qt(pgm_data)
        self.setImage(qtimg)

class ModellingWindow(QWidget):
    """"""
    # self-defined pyqtSignal, 0 - new or failed, 1 - successful
    modeling_ok = pyqtSignal(int, object)  # object: model data(np array)
    originFileChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        """Constructor"""
        super().__init__(parent=parent)


        lo = QGridLayout()
        self.setLayout(lo)

        self.originLabel = QLabel('Origin')
        edgeLabel = QLabel('Edge')
        self.binaryLabel = QLabel('Threshold')

        self.openBtn = QPushButton('Open')
        self.thresholdEdit = QLineEdit()
        self.thresholdEdit.setFixedWidth(60)
        self.thresholdEdit.setText('60')
        self.thresholdEdit.setToolTip('press Enter key to update')

        # image windows
        self.originWin = ImageWindow()
        self.edgeWin = ImageWindow()
        self.binaryWin = ImageWindow()

        # skin and illness/rotten
        skinLabel = QLabel('skin thickness:')
        self.skin_thicknessEdit = QLineEdit('0')
        self.skin_thicknessEdit.setFixedWidth(60)
        self.skin_thicknessEdit.setToolTip('range 1-10')
        
        self.rottenBtn = QRadioButton('illness/rotten')

        self.modellingBtn = QPushButton('3D-Model')

        # int fromRow, int fromColumn, int rowSpan, int columnSpan
        lo.addWidget(self.originLabel, 0, 0, 1, 1)
        lo.addWidget(self.openBtn, 0, 1, 1, 1, Qt.AlignRight)
        lo.addWidget(edgeLabel, 0, 2, 1, 1)
        lo.addWidget(self.binaryLabel, 0, 3, 1, 1, Qt.AlignRight)
        lo.addWidget(self.thresholdEdit, 0, 4, 1, 1, Qt.AlignLeft)

        lo.addWidget(self.originWin, 1, 0, 1, 2)
        lo.addWidget(self.edgeWin, 1, 2, 1, 1)
        lo.addWidget(self.binaryWin, 1, 3, 1, 2)

        lo.addWidget(skinLabel, 2, 1, 1, 1)
        lo.addWidget(self.skin_thicknessEdit, 2, 2, 1, 1)
        lo.addWidget(self.rottenBtn, 2, 3, 1, 1, Qt.AlignCenter)

        lo.addWidget(self.modellingBtn, 3, 3, 1, 2, Qt.AlignCenter)

        # slots
        self.openBtn.clicked.connect(self.openFile)
        self.thresholdEdit.returnPressed.connect(self.thresholdChanged)
        self.modellingBtn.clicked.connect(self.modelBuild)

        # setting
        self.updateFile('images/p6.png')

    def openFile(self):
        """"""
        file, _ = QFileDialog.getOpenFileName(self, 'Open image file', 'images', 'Image files (*.png *.jpg *.jpeg)')

        if file != '':
            self.updateFile(file)
            self.model = None
            self.modeling_ok.emit(0, self.model)

    def updateFile(self, file):

        self.originWin.setFile(file)
        #self.originLabel.setText(f'Origin [{file[:6]}...{file[-9:]}]')
        #self.parent().parent().setWindowTitle(f"Simulation of Avocado - {file}")
        self.originFileChanged.emit(file)

        img = edge(self.originWin.cvimg)
        self.edgeWin.setImage(self.edgeWin.cvimg2Qt(img))

        self.thresholdChanged()

    def thresholdChanged(self):
        """"""
        val = int(self.thresholdEdit.text())

        img = edge(self.originWin.cvimg)
        self.edgeWin.setImage(self.edgeWin.cvimg2Qt(img))

        img = binary(img, threshold=val)
        self.binaryWin.setImage(self.binaryWin.cvimg2Qt(img))
        self.binaryWin.cvimg = img

    def modelBuild(self):
        """"""
        # if rotten
        if self.rottenBtn.isChecked():
            rotten = True
        else:
            rotten = False

        # skin_thickness
        skin_thickness = int(self.skin_thicknessEdit.text())
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        # start get radius, offset
        model = model3D(self.binaryWin.cvimg, skin_thickness, rotten)

        QApplication.restoreOverrideCursor()
        
        if model is not None:
            # emit pyqtSignal
            self.modeling_ok.emit(1, model)

        else:
            QMessageBox.information(self, 'modeling', 'modeling failed')
            
        

class PgmWindow(QWidget):
    """"""

    def __init__(self, parent=None):
        """Constructor"""
        super().__init__(parent=parent)
        self.model = None

        PGMLayOut = QGridLayout(self)
        # image labels
        self.TopLabel = QLabel('Top View')
        self.SideLabel = QLabel('Side View')
        self.FrontLabel = QLabel('Front View')

        self.X_axisLabel = QLabel('X-cor:')
        self.Y_axisLabel = QLabel('Y-cor:')
        self.Z_axisLabel = QLabel('Z-cor:')

    # PGM image windows
        self.X_PGM = ImageWindow()
        self.Y_PGM = ImageWindow()
        self.Z_PGM = ImageWindow()
        self.X_PGM.setStyleSheet("border: 1px solid black;")
        self.Y_PGM.setStyleSheet("border: 1px solid black;")
        self.Z_PGM.setStyleSheet("border: 1px solid black;")

    # coordinate
        self.X_cor = QLineEdit()
        self.Y_cor = QLineEdit()
        self.Z_cor = QLineEdit()

        self.X_cor.setFixedWidth(60)
        self.Y_cor.setFixedWidth(60)
        self.Z_cor.setFixedWidth(60)

        # layout
        PGMLayOut.addWidget(self.FrontLabel, 0, 0, 1, 2)
        PGMLayOut.addWidget(self.SideLabel, 0, 2, 1, 2)
        PGMLayOut.addWidget(self.TopLabel, 0, 4, 1, 2)
        
        PGMLayOut.addWidget(self.X_PGM, 1, 0, 1, 2)
        PGMLayOut.addWidget(self.Y_PGM, 1, 2, 1, 2)
        PGMLayOut.addWidget(self.Z_PGM, 1, 4, 1, 2)        
        
        PGMLayOut.addWidget(self.X_axisLabel, 2, 0, 1, 1, Qt.AlignRight)
        PGMLayOut.addWidget(self.Y_axisLabel, 2, 2, 1, 1, Qt.AlignRight)
        PGMLayOut.addWidget(self.Z_axisLabel, 2, 4, 1, 1, Qt.AlignRight)

        PGMLayOut.addWidget(self.X_cor, 2, 1, 1, 1, Qt.AlignLeft)
        PGMLayOut.addWidget(self.Y_cor, 2, 3, 1, 1, Qt.AlignLeft)
        PGMLayOut.addWidget(self.Z_cor, 2, 5, 1, 1, Qt.AlignLeft)

        # slot
        self.X_cor.returnPressed.connect(self.X_cor_Changed)
        self.Y_cor.returnPressed.connect(self.Y_cor_Changed)
        self.Z_cor.returnPressed.connect(self.Z_cor_Changed)

    def modelReset(self, model):
        """"""
        self.model = model
        zl, xl, yl = model.shape
        
        self.X_axisLabel.setText(f'x-cor[0,{xl}]:')
        self.Y_axisLabel.setText(f'y-cor[0,{yl}]:')
        self.Z_axisLabel.setText(f'z-cor[0,{zl}]:')

    def X_cor_Changed(self):
        x = self.X_cor.text()
        self.FrontLabel.setText(f'Front View(x = {x})')
        pgm = self.model[:, int(x), :]
        self.X_PGM.setPgm(pgm)
        
    def Y_cor_Changed(self):
        y = self.Y_cor.text()
        self.SideLabel.setText(f'Side View(y = {y})')        
        pgm = self.model[:, :, int(y)]
        self.Y_PGM.setPgm(pgm)

    def Z_cor_Changed(self):
        z = self.Z_cor.text()
        self.TopLabel.setText(f'Top View(z = {self.Z_cor.text()})')        
        pgm = self.model[int(z), :, :]
        self.Z_PGM.setPgm(pgm)
