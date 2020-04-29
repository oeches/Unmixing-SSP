#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""main GUI for synthetic pixel"""
"""connecting the buttons for unmixing"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot
from numpy import zeros, random
from sys import stderr
import src.UIfensynthpixel as uif
import src.FenDisplayResults as fDisp
import lib.modelImage as mI
import lib.modelGraph as mG
import src.unmixing as unmix

class FenSynthPixelClass(QWidget):
    """Synth pixel configuration window"""
    def __init__(self, parent=None):
        """Class initialization"""
        super().__init__(parent)
        self.numbEndm = 2
        self.numbMaxEndm = 6
        self.libFile = ""
        self.boolSpectraLoaded = False
        self.winRes = None
        self.msgError = ""
        self._test_warning = None
        self.ui = uif.Ui_FenSynthPixel()
        self.ui.setupUi(self)
        #self.ui.lineEditLib.setReadOnly(True)
        self.ui.RadioButtonGroup.setId(self.ui.radioButtR2,0)
        self.ui.RadioButtonGroup.setId(self.ui.radioButtR3,1)
        self.ui.RadioButtonGroup.setId(self.ui.radioButtR4,2)
        self.ui.RadioButtonGroup.setId(self.ui.radioButtR5,3)
        self.ui.RadioButtonGroup.setId(self.ui.radioButtR6,4)
        self.pxSynth = mI.PixelSynth()
        
        self.ui.lineEditLib.editingFinished.connect(self.textHasChanged)
        self.ui.ButtonBrowseLib.clicked.connect(self.BrowseLib)

    @pyqtSlot()
    def BrowseLib(self):
        """Browse library file when clicked"""
        libFileTup = QFileDialog.getOpenFileName(self, "Open spectral library", "", "Data files (*.npy)")
        self.libFile = libFileTup[0]
        if self.libFile:
            self.ui.lineEditLib.setText(self.libFile)
            self.checkLoadSpectraLib()
        else:
            self.boolSpectraLoaded = False

    @pyqtSlot()
    def textHasChanged(self):
        """Happens when the line edit text finished, when the lib file has been chosen"""
        self.libFile = self.ui.lineEditLib.text()
        if self.libFile:
            self.checkLoadSpectraLib()
        else:
            self.boolSpectraLoaded = False

    @pyqtSlot(int)
    def on_RadioButtonGroup_buttonClicked(self, id):
        """choose the number of endmembers and grey the corresponding spin boxes"""
        #id_logic = [False for i in range(4)] #initialization
        dict_switch = {
        0 : [False, False, False, False],
        1 : [True, False, False, False],
        2 : [True, True, False, False],
        3 : [True, True, True, False],
        4 : [True, True, True, True],
        }
        id_logic = dict_switch.get(id, [False, False, False, False])
        self.enableSpinBoxes(id_logic)
        self.numbEndm = 2 + id

    @pyqtSlot()
    def on_ButtonGenerate_clicked(self):
        """Generate Random abundances"""
        abDisplay = zeros((self.numbMaxEndm,1)) # maximum number of abundances fixed to self.numbMaxEndm
        abDisplay[0:self.numbEndm] = random.rand(self.numbEndm, 1)
        sumAb = sum(abDisplay)
        abDisplay = abDisplay/sumAb
        abDisplay[self.numbEndm - 1] = 1 - sum(abDisplay[0:self.numbEndm-1])
        # display
        self.ui.a_1DoubleSpinBox.setValue(abDisplay[0])
        self.ui.a_2DoubleSpinBox.setValue(abDisplay[1])
        self.ui.a_3DoubleSpinBox.setValue(abDisplay[2])
        self.ui.a_4DoubleSpinBox.setValue(abDisplay[3])
        self.ui.a_5DoubleSpinBox.setValue(abDisplay[4])
        self.ui.a_6DoubleSpinBox.setValue(abDisplay[5])

    @pyqtSlot()
    def on_ButtonUnmix_clicked(self):
        """Lauching the unmixing process"""
        # check if spectra is loaded
        try:
            if self.boolSpectraLoaded == False:
                raise Warning("Please load the spectra first")
        except Warning:
            self.msgError = "Please load the spectra first"
            QMessageBox.warning(self, "No Spectra", self.msgError)
            #stderr.write("Please load the spectra first")
            return

        # Abundances
        abRead = zeros((self.numbMaxEndm,1))
        abRead[0] = self.ui.a_1DoubleSpinBox.value()
        abRead[1] = self.ui.a_2DoubleSpinBox.value()
        abRead[2] = self.ui.a_3DoubleSpinBox.value()
        abRead[3] = self.ui.a_4DoubleSpinBox.value()
        abRead[4] = self.ui.a_5DoubleSpinBox.value()
        abRead[5] = self.ui.a_6DoubleSpinBox.value()

        abundancesInput = abRead[0:self.numbEndm]

        sumRes = sum(abundancesInput)
        try:
            if sumRes != 1:
                raise ValueError("Problem with generated abundances : sum equal to {}".format(sumRes))
        except ValueError:
            self.msgError = "Please ensure the sum of abundances equal to 1"
            QMessageBox.warning(self, "Abundances coefficients !", self.msgError)
            #stderr.write("Please ensure the sum of abundances equal to 1")
            return

        #sampling step for spectra band number
        SamplingStep = 2
        #NoiseVariance
        sigNoise = self.ui.noiseVarianceDoubleSpinBox.value()

        self.pxSynth.generateSynthPixel(self.numbEndm, SamplingStep, abundancesInput, sigNoise)
        Nmc = self.ui.iterationsSpinBox.value()
        Nbi = self.ui.burnInSpinBox.value()

        #Unmixing
        TAlphaPlus, TSigma2r, boolAbort = unmix.unmixPixel(self.pxSynth, Nmc)

        #Results
        if boolAbort == False:
            #myHistogramVar = mG.HistogramSamples(2,50)
            myHistogramAbund = mG.HistogramSamples(1,50)
        
            meanAbund, fighandleAbund = myHistogramAbund.compute(Nmc, Nbi, TAlphaPlus, "Abundances", self.numbEndm)
            #meanNoise, fighandleNoise = myHistogramVar.compute(Nmc, Nbi, TSigma2r, "Variance", 1)

            self.winRes = fDisp.FenDisplayResults(fighandleAbund, meanAbund, self.numbEndm)
            self.winRes.exec()

    def checkLoadSpectraLib(self):
        """Call this function to load and check the Spectral lib file"""
        try:
            MaxEndmLib = self.pxSynth.loadSpectraLib(self.libFile)
            if MaxEndmLib <= 1:
                raise ValueError("Too few spectra")
        except Warning:
            self.msgError = "Please select a correct npy file that contains spectra data"
            QMessageBox.warning(self, "Wrong npy file", self.msgError)
            self._test_warning = QtWidgets.QApplication.activeWindow()
            #stderr.write('Please select a correct npy file that contains spectra data')
            self.boolSpectraLoaded = False
            return
        except ValueError:
            self.msgError = "Please select a npy file that contains at least 2 spectra"
            QMessageBox.warning(self, "Too few spectra", self.msgError)
            #stderr.write('Please select a npy file that contains at least 2 spectra')
            self.boolSpectraLoaded = False
            return

        if MaxEndmLib > self.numbMaxEndm:
            MaxEndmLib = self.numbMaxEndm #we do not allow more than 6 spectra, the first 6 are used

        dict_switch_disable = {
        2 : [False, False, False, False],
        3 : [True, False, False, False],
        4 : [True, True, False, False],
        5 : [True, True, True, False],
        6 : [True, True, True, True],
        }

        id_logic = dict_switch_disable.get(MaxEndmLib, [False, False, False, False])
        self.enableRadioButton(id_logic)
        self.boolSpectraLoaded = True

    def enableRadioButton(self, id_logic):
        """Enable or disable radio buttons"""
        self.ui.radioButtR3.setEnabled(id_logic[0])
        self.ui.radioButtR4.setEnabled(id_logic[1])
        self.ui.radioButtR5.setEnabled(id_logic[2])
        self.ui.radioButtR6.setEnabled(id_logic[3])

    def enableSpinBoxes(self, id_logic):
        """Enable or disable spinboxes"""
        self.ui.a_3DoubleSpinBox.setEnabled(id_logic[0])
        self.ui.a_4DoubleSpinBox.setEnabled(id_logic[1])
        self.ui.a_5DoubleSpinBox.setEnabled(id_logic[2])
        self.ui.a_6DoubleSpinBox.setEnabled(id_logic[3])


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FenSynthPixel_win = FenSynthPixelClass()
    FenSynthPixel_win.show()
    sys.exit(app.exec_())
