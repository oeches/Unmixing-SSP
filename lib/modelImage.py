#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Class Image and PixelSynth"""
import re
import numpy as np

class Image:
    """Class Image to load the ROI and extract the pixel values"""
    def __init__(self):
        """Class initialization"""
        self.DimensionX = 1
        self.DimensionY = 1
        self.SpectralBands = 1
        self.EndmembersNumber = 1
        self.Wavelength = np.zeros((self.SpectralBands))
        self.EndmembersMatrix = np.zeros((self.SpectralBands, self.EndmembersNumber))
        self.imageBands = np.zeros((self.DimensionX, self.DimensionY, self.SpectralBands))
        self.PixelValues = np.zeros((self.DimensionX * self.DimensionY, self.SpectralBands))
        self.SpectralValues = np.zeros((1,1))

    def loadImage(self, filename):
        """Method that load the image stored in a NPY file"""
        """We expect the NPY file to contain a dictionnary containing"""
        """the key "image" (the hyperspectral ROI) and the key "mask" """
        """that contains the mask hiding the water absorption bands"""
        try:
            name_npy = re.search(r'^.+\.(\D{3})$', filename)
            ext = name_npy.group(1)
            if ext == 'npy':
                # load image data
                data_npy = np.load(filename, None, True)
            else:
                raise Warning('Indicate a .npy file for image')
        except FileNotFoundError as name_npy:
            raise Warning('Indicate a file that exists !')

        if data_npy.ndim == 0:
            data_npy = np.atleast_1d(data_npy)

        #check if it has the correct fields
        try: 
            listKeys = list(data_npy[0].keys())
            if "image" in listKeys and "mask" in listKeys:
                imageTemp = data_npy[0]["image"]
                mask = data_npy[0]["mask"]
            else:
                raise Warning('Error with file chosen : Use a npy file containing image data')
        except Warning as e:
            raise Warning(e)
        
        # we expect a tuple (Nli, Ncol, Nspectralbands) as a result of .shape()
        sizeOfImage = np.shape(imageTemp)
        self.DimensionX = sizeOfImage[0]
        self.DimensionY = sizeOfImage[1]
        spectralBandsTemp = sizeOfImage[2]
        imageTemp = np.reshape(imageTemp, (self.DimensionX * self.DimensionY, spectralBandsTemp))

        self.SpectralBands = len(mask[mask == 1])
        # We apply the mask
        maskMatrix = np.tile(mask,(self.DimensionX * self.DimensionY, 1))
        maskImage = imageTemp[maskMatrix == 1]
        self.imageBands = np.reshape(maskImage, (self.DimensionX, self.DimensionY, self.SpectralBands))
        self.PixelValues = np.reshape(self.imageBands, (self.DimensionX * self.DimensionY, self.SpectralBands))
        self.PixelValues = np.transpose(self.PixelValues)

    def extractPixel(self, index):
        """Method that return a given pixel from the current image"""
        self.SpectralValues = self.PixelValues[:,index]

    def loadImageSpectra(self, filename):
        """Method that loads the endmembers of the current ROI from a npy file and fix their number"""
        try:
            name_npy = re.search(r'^.+\.(\D{3})$', filename)
            ext = name_npy.group(1)
            if ext == 'npy':
                # load image data
                data_npy = np.load(filename, None, True)
            else:
                raise Warning('Indicate a .npy file for spectra')
        except FileNotFoundError as name_npy:
            raise Warning('Indicate a file that exists !')

        if data_npy.ndim == 0:
            data_npy = np.atleast_1d(data_npy)

        #check if it has the correct fields
        try: 
            listKeys = list(data_npy[0].keys())
            if "Wavelength" in listKeys and "spectra" in listKeys:
                self.Wavelength = data_npy[0]["Wavelength"]
                self.EndmembersMatrix = data_npy[0]["spectra"]
            else:
                raise Warning('Error with file chosen : Use a npy file containing spectra data')
        except Warning as e:
            raise Warning(e)

        sizeofEndmembersMatrix = np.shape(self.EndmembersMatrix)
        self.EndmembersNumber = sizeofEndmembersMatrix[1]
        return self.EndmembersNumber


class PixelSynth:
    """Class PixelSynth that creates a single synthetic Pixel for validation tests"""
    def __init__(self):
        """Class Initialization"""
        self.EndmembersNumber = 1
        self.Abundances = np.zeros((self.EndmembersNumber,1))
        self.EndmembersMatrix = np.zeros((1,self.EndmembersNumber))
        self.Wavelength = np.zeros((1))
        self.SpectralLibrary = np.zeros((1,1))
        self.SpectralValues = np.zeros((1,1))

    def loadSpectraLib(self, filename):
        """Loading the spectral library included in npy file"""
        """return the number of spectra in the lib file"""
        try:
            name_npy = re.search(r'^.+\.(\D{3})$', filename)
            ext = name_npy.group(1)
            if ext == 'npy':
                # load image data
                data_npy = np.load(filename, None, True)
            else:
                raise Warning('Indicate a .npy file for image')
        except FileNotFoundError as name_npy:
            raise Warning('Indicate a file that exists !')

        if data_npy.ndim == 0:
            data_npy = np.atleast_1d(data_npy)

        #check if it has the correct fields
        try: 
            listKeys = list(data_npy[0].keys())
            if "Wavelength" in listKeys and "spectra" in listKeys:
                self.Wavelength = data_npy[0]["Wavelength"]
                self.SpectralLibrary = data_npy[0]["spectra"]
            else:
                raise Warning('Error with file chosen : Use a npy file containing spectra data')
        except Warning as e:
            raise Warning(e)

        sizeOfSpectralLib = np.shape(self.SpectralLibrary)
        return sizeOfSpectralLib[1]

    def generateSynthPixel(self, endmembersNumber, samplingStep, Abundances, noiseVariance):
        """Generating the synthetic pixel according to NCM from the GUI"""
        self.EndmembersNumber = endmembersNumber
        self.Abundances = Abundances
        if self.Abundances.size != self.EndmembersNumber:
            raise ValueError('Wrong number of endmember')

        indexEndmChosen = range(self.EndmembersNumber)
        self.EndmembersMatrix = self.SpectralLibrary[0:-1:samplingStep, indexEndmChosen]
        self.Wavelength = self.Wavelength[0:-1:samplingStep] 

        # generating the pixel from a multivariate gaussian distribution
        # covariance matrix = size of number of bands
        noiseVec = np.dot((noiseVariance * np.eye(self.EndmembersNumber)), np.ones((self.EndmembersNumber,1)))
        numBandes = np.shape(self.EndmembersMatrix)
        numBandes = numBandes[0]

        # in a loop, generate M+, random endmember matrix from the NCM
        endmembersRandMatrix = np.zeros((numBandes, self.EndmembersNumber))
        for indEndm in indexEndmChosen:
            endmembersRandMatrix[:,indEndm] = np.random.multivariate_normal(
                self.EndmembersMatrix[:,indEndm], noiseVec[indEndm]*np.eye(numBandes))

        #finally, the pixel :
        self.SpectralValues = np.dot(endmembersRandMatrix,self.Abundances)


    def generateSynthPixel_old(self, endmembersNumber, samplingStep, noiseVariance):
        """Generating the synthetic pixel according to NCM"""
        """abundances are randomly generated on the Simplex"""
        """Old Version"""
        self.EndmembersNumber = endmembersNumber
        sizeOfSpectralLib = np.shape(self.SpectralLibrary)
        MaxEndmembers = sizeOfSpectralLib[1]
        #Up to (size of the library) endmembers to be chosen
        if self.EndmembersNumber > MaxEndmembers:
            raise ValueError('Choose a number of endmember less than {}'.format(MaxEndmembers))

        indexEndmChosen = range(self.EndmembersNumber)
        self.EndmembersMatrix = self.SpectralLibrary[0:-1:samplingStep, indexEndmChosen]
        self.Wavelength = self.Wavelength[0:-1:samplingStep] 

        # generating abundances for this pixel 
        self.Abundances = np.zeros((self.EndmembersNumber,1))
        vecAbund = np.random.rand(self.EndmembersNumber, 1)
        sumVecAbund = np.sum(vecAbund)
        vecAbund = vecAbund/sumVecAbund
        self.Abundances = vecAbund
        self.Abundances[self.EndmembersNumber-1] = 1 - np.sum(vecAbund[0:self.EndmembersNumber-1])

        # generating the pixel from a multivariate gaussian distribution
        # covariance matrix = size of number of bands
        noiseVec = np.dot((noiseVariance * np.eye(self.EndmembersNumber)), np.ones((self.EndmembersNumber,1)))
        numBandes = np.shape(self.EndmembersMatrix)
        numBandes = numBandes[0]

        # in a loop, generate M+, random endmember matrix from the NCM
        endmembersRandMatrix = np.zeros((numBandes, self.EndmembersNumber))
        for indEndm in indexEndmChosen:
            endmembersRandMatrix[:,indEndm] = np.random.multivariate_normal(
                self.EndmembersMatrix[:,indEndm], noiseVec[indEndm]*np.eye(numBandes))

        #finally, the pixel :
        self.SpectralValues = np.dot(endmembersRandMatrix,self.Abundances)

    def getBandsNumber(self):
        sizeofbandsNumber = np.shape(self.SpectralValues)
        bandsNumber = sizeofbandsNumber[0]
        return bandsNumber


if __name__ == "__main__":
    pass
else:
    print("Importation of modelImage.py...")







