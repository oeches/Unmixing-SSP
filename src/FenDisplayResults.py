#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dialog that opens to display abundance results"""
"""Possibility to show the histograms"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSlot
import matplotlib as mil
mil.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#class MplCanvas(FigureCanvasQTAgg):
#
#    def __init__(self, parent=None, width=5, height=4, dpi=100):
#        fig = Figure(figsize=(width, height), dpi=dpi)
#        self.axes = fig.add_subplot(111)
#        super(MplCanvas, self).__init__(fig)

class FenDisplayResults(QDialog):
    """class for the window displaying results"""
    def __init__(self, figHandle, abundMeans, numbEndm, parent=None):
        """Constructor"""
        super().__init__(parent)
        self.figHandle = figHandle
        self.abundMeans = abundMeans

        self.setWindowTitle("Abundance results (means)")
        self.mainLayout = QVBoxLayout()
        self.resultsDispText = QLabel()
        self.resultsDispText.setAlignment(Qt.AlignCenter)
        self.buttonQuit = QPushButton("Quit")
        self.mainLayout.addWidget(self.resultsDispText)
        self.mainLayout.addWidget(self.buttonQuit)
        self.canvas = FigureCanvasQTAgg(self.figHandle)
        #sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.mainLayout.addWidget(self.canvas)
        
        self.setLayout(self.mainLayout)
        self.displayText(numbEndm)
        
        self.buttonQuit.clicked.connect(self.closeIt)

    @pyqtSlot()
    def closeIt(self): 
        self.close()

    def displayText(self, numbEndm):
        """function that display the text label"""
        text2Disp = ""
        for i in list(range(numbEndm)):
            text2Disp += "a_{} = {} \n".format(i+1, self.abundMeans[i])

        self.resultsDispText.setText(text2Disp)

