#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""main GUI for real image"""
"""connecting the buttons for unmixing"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtCore import pyqtSlot
import src.UIFenImageHyper as uif
import src.FenDisplayResults as fDisp
import lib.modelImage as mI
import lib.modelGraph as mG
from numpy import mean, zeros, transpose
import src.unmixing as unmix

class FenRealImageClass(QWidget):
    """Real image configuration window"""
    def __init__(self, parent=None):
        """Class initialization"""
        super().__init__(parent)
        self.imageFile = ""
        self.libFile = ""
        self.ui = uif.Ui_FenImageHyper()
        self.ui.setupUi(self)
        self.imageHyper = mI.Image()
        self.boolSpectraLoaded = False
        self.boolImageLoaded = False
        self.msgError = ""

        self.ui.lineEditSpectralLib.editingFinished.connect(self.textHasChangedLib)
        self.ui.ButtonBrowseLib.clicked.connect(self.BrowseLib)

        self.ui.lineEditImage.editingFinished.connect(self.textHasChangedImage)
        self.ui.ButtonBrowseIm.clicked.connect(self.BrowseIm)

    @pyqtSlot()
    def BrowseLib(self):
        """Browse library file when clicked"""
        libFileTup = QFileDialog.getOpenFileName(self, "Open spectral library", "", "Data files (*.npy)")
        self.libFile = libFileTup[0]
        if self.libFile:
            self.ui.lineEditSpectralLib.setText(self.libFile)
            self.checkLoadSpectraLib()
        else:
            self.boolSpectraLoaded = False

    @pyqtSlot()
    def textHasChangedLib(self):
        """Happens when the spectra line edit text finished, when the lib file has been chosen"""
        self.libFile = self.ui.lineEditSpectralLib.text()
        if self.libFile:
            self.checkLoadSpectraLib()
        else:
            self.boolSpectraLoaded = False

    @pyqtSlot()
    def BrowseIm(self):
        """Browse image file when clicked"""
        imageFileTup = QFileDialog.getOpenFileName(self, "Open image file", "", "Data files (*.npy)")
        self.imageFile = imageFileTup[0]
        if self.imageFile:
            self.ui.lineEditImage.setText(self.imageFile)
            self.checkLoadImage()
        else:
            self.boolImageLoaded = False

    @pyqtSlot()
    def textHasChangedImage(self):
        """Happens when the image line edit text finished, when the image file has been chosen"""
        self.imageFile = self.ui.lineEditImage.text()
        if self.imageFile:
            self.checkLoadImage()
        else:
            self.boolImageLoaded = False

    @pyqtSlot()
    def on_ButtonUnmix_clicked(self):
        """Lauching the unmixing process"""
        # check if image is loaded
        try:
            if self.boolImageLoaded == False:
                raise Warning("Please load the image first")
        except Warning:
            self.msgError  = "Please load the image first"
            QMessageBox.warning(self, "No Image", self.msgError)
            return

        # check if spectra is loaded
        try:
            if self.boolSpectraLoaded == False:
                raise Warning("Please load the spectra first")
        except Warning:
            self.msgError = "Please load the spectra first"
            QMessageBox.warning(self, "No Spectra", self.msgError)
            return

        Nmc = self.ui.iterationsSpinBox.value()
        Nbi = self.ui.burnInSpinBox.value()

        numPixels = self.imageHyper.DimensionX * self.imageHyper.DimensionY

        progressIm = QProgressDialog("Unmixing image", "Abort", 0, numPixels)
        progressIm.setModal(True)
        boolAbortImage = False
        meanOfSamples = zeros((self.imageHyper.EndmembersNumber,numPixels))

        for indPx in list(range(numPixels)):
            #unmix each pixel
            self.imageHyper.extractPixel(indPx)
            #Unmixing
            TAlphaPlus, TSigma2r, boolAbort = unmix.unmixPixel(self.imageHyper, Nmc)

            meanOfSamples[:,indPx] = transpose(mean(TAlphaPlus.getNSamples(Nmc-Nbi+1,Nbi), axis=1))

            progressIm.setValue(indPx)
            if progressIm.wasCanceled() or boolAbort==True:
                boolAbortImage = True
                break

        progressIm.setValue(numPixels)

        if boolAbortImage == False:
            #results...
            resAb = mG.AbundanceMaps(self.imageHyper.EndmembersNumber, self.imageHyper.DimensionX, self.imageHyper.DimensionY)
            resAb.show(meanOfSamples)


    def checkLoadSpectraLib(self):
        """Call this function to load and check the Spectral lib file"""
        try:
            MaxEndmLib = self.imageHyper.loadImageSpectra(self.libFile)
            if MaxEndmLib <= 1:
                raise ValueError("Too few spectra")
        except Warning:
            self.msgError = "Please select a correct npy file that contains spectra data"
            QMessageBox.warning(self, "Wrong npy file", self.msgError)
            return
        except ValueError:
            self.msgError = "Please select a npy file that contains at least 2 spectra"
            QMessageBox.warning(self, "Too few spectra", self.msgError)
            return

        self.boolSpectraLoaded = True

    def checkLoadImage(self):
        """Call this function to load and check the image file"""
        try:
            self.imageHyper.loadImage(self.imageFile)
        except Warning:
            self.msgError = "Please select a correct npy file that contains image data"
            QMessageBox.warning(self, "Wrong npy file", self.msgError)
            return

        self.boolImageLoaded = True


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FenRealImage_win = FenRealImageClass()
    FenRealImage_win.show()
    sys.exit(app.exec_())