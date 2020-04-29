#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""main GUI for launching unmixing """
"""images not ready yet"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSlot
import src.FenSynthPixelClass as fenClass
import src.FenRealImageClass  as fenReal

class FenPrimaryClass(QWidget):
    """Class for the primary window where we choose what to unmix"""
    def __init__(self, parent=None):
        """Constructor"""
        super().__init__(parent)
        self.setWindowTitle("What do you want to Unmix ?")
        mainLayout = QHBoxLayout()
        self.buttonImage = QPushButton("Unmix image")
        self.buttonSynthPixel = QPushButton("Unmix synthetic pixel")
        mainLayout.addWidget(self.buttonImage)
        mainLayout.addWidget(self.buttonSynthPixel)
        self.setLayout(mainLayout)
        self.winSynth = None
        self.winReal = None

        self.buttonImage.clicked.connect(self.unmixRealImage)
        self.buttonSynthPixel.clicked.connect(self.generateSynthPixel)

    @pyqtSlot()
    def unmixRealImage(self):
        """launching the real image window"""
        self.winReal = fenReal.FenRealImageClass()
        self.winReal.setWindowModality(QtCore.Qt.ApplicationModal)
        self.winReal.show()

    @pyqtSlot()
    def generateSynthPixel(self):
        """launching the synthetic pixel window"""
        self.winSynth = fenClass.FenSynthPixelClass()
        self.winSynth.setWindowModality(QtCore.Qt.ApplicationModal)
        self.winSynth.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FenPrim_win = FenPrimaryClass()
    FenPrim_win.show()
    sys.exit(app.exec_())