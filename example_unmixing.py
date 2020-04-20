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

    myPixelSynth.generateSynthPixel_old(NumEnd, SamplingStep, sigNoise)

    print("Bands number : {}".format(myPixelSynth.getBandsNumber()))
    print("Number of Endmembers : {}, Abundances : {}".format(myPixelSynth.EndmembersNumber, myPixelSynth.Abundances))
    print("Dim spectral values : {}".format(np.shape(myPixelSynth.SpectralValues)))
    print("Shape of endmember matrix : {}".format(np.shape(myPixelSynth.EndmembersMatrix)))

	# check if sum equal to 1
    ind = 0
    sumRes = np.sum(myPixelSynth.Abundances)
    while sumRes != 1:
        print("Problem with generated abundances : sum equal to {}, adjusting...".format(sumRes))
        epsilon = sumRes - 1
        if epsilon > 0:
            myPixelSynth.Abundances[NumEnd-1] = myPixelSynth.Abundances[NumEnd-1] - epsilon
        else:
            myPixelSynth.Abundances[NumEnd-1] = myPixelSynth.Abundances[NumEnd-1] + epsilon
        sumRes = np.sum(myPixelSynth.Abundances)
        ind += 1
        if ind > 10:
            break #avoiding infinite loop

    #unmix single pixel
    Nmc = 5000
    Nbi = 1000

    TAlphaPlus, TSigma2r = unmixing.unmixPixel(myPixelSynth, Nmc)

    # displaying histograms

    myHistogramVar = mG.HistogramSamples(2,50)
    myHistogramAbund = mG.HistogramSamples(1,50)
    
    meanAbund, fighandleAbund = myHistogramAbund.compute(Nmc, Nbi, TAlphaPlus, "Abundances", NumEnd)
    meanNoise, fighandleNoise = myHistogramVar.compute(Nmc, Nbi, TSigma2r, "Variance", 1)

    fighandleAbund.show()
    fighandleNoise.show()

    input()

if __name__ == "__main__":
    main()