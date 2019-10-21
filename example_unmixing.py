#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Example for a single pixel"""
import numpy as np
import lib.modelGraph as mG
import lib.modelImage as mI
import unmixing

def main():
    
	# setting random seed
    np.random.seed(2)

	#loading spectra from database
    myPixelSynth = mI.PixelSynth()
    myPixelSynth.loadSpectraLib("data/spectraSynth_dict.npy")

    #number of endmembers
    NumEnd = 3
    #sampling step for spectra band number
    SamplingStep = 2
    #NoiseVariance
    sigNoise = 0.001

    myPixelSynth.generateSynthPixel(NumEnd, SamplingStep, sigNoise)

    print("Bands number : {}".format(myPixelSynth.getBandsNumber()))
    print("Number of Endmembers : {}, Abundances : {}".format(myPixelSynth.EndmembersNumber, myPixelSynth.Abundances))
    print("Dim spectral values : {}".format(np.shape(myPixelSynth.SpectralValues)))
    print("Shape of endmember matrix : {}".format(np.shape(myPixelSynth.EndmembersMatrix)))

	# check if sum equal to 1
    sumRes = np.sum(myPixelSynth.Abundances)
    if sumRes != 1:
        raise Exception("Problem with generated abundances : sum equal to {}".format(sumRes))

    #unmix single pixel
    Nmc = 5000
    Nbi = 1000

    TAlphaPlus, TSigma2r = unmixing.unmixPixel(myPixelSynth, Nmc)

    # displaying histograms

    myHistogramVar = mG.HistogramSamples(2,50)
    myHistogramAbund = mG.HistogramSamples(1,50)
    
    myHistogramAbund.show(Nmc, Nbi, TAlphaPlus, "Abundances", NumEnd)
    myHistogramVar.show(Nmc, Nbi, TSigma2r, "Variance", 1)

    input()

if __name__ == "__main__":
    main()