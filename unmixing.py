#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import lib.modelMCMC as mMCMC
from progress.bar import Bar

def unmixPixel(imagePixel, chainLength):
    # reminder : #import pdb; pdb.set_trace() in debug mode !

    # hyperparameter
    delta = 0.001
    # endmember variance 
    sigma2r = 0.001*np.ones((1,imagePixel.EndmembersNumber))
    sigma2rSamples = mMCMC.Samples(imagePixel.EndmembersNumber, "Endmember variance", sigma2r)
    # abundance vector
    abundance = np.ones((imagePixel.EndmembersNumber,1))/imagePixel.EndmembersNumber
    abundanceSamples = mMCMC.Samples(imagePixel.EndmembersNumber, "Abundances", abundance)
    # boolean 
    rho = np.zeros((1,imagePixel.EndmembersNumber))
    rhoSamples = mMCMC.Samples(imagePixel.EndmembersNumber, "Boolean", rho)

    #useful quantities
    sig = 0.05*np.ones((1,imagePixel.EndmembersNumber))
    Tx = 0.3*np.ones((imagePixel.EndmembersNumber,1))
    vecRhoSamples = np.zeros((imagePixel.EndmembersNumber,100))

    #initializing chains
    TRho = mMCMC.MCMCChains(chainLength, imagePixel.EndmembersNumber, "Acceptation rate chain")
    TRho.FillInitialSamples(rho)
    TAlphaPlus = mMCMC.MCMCChains(chainLength, imagePixel.EndmembersNumber, "Abundances chain")
    TAlphaPlus.FillInitialSamples(abundance)
    TSigma2r = mMCMC.MCMCChains(chainLength, imagePixel.EndmembersNumber, "Endmember variance chain")
    TSigma2r.FillInitialSamples(sigma2r)

    #initializing samplers
    sampleAbund = mMCMC.MwG_abundances(Tx, sig, 0.5)
    sampleVar = mMCMC.GibbsForVariance()
    sampleDelta = mMCMC.GibbsForHyperparameter()

    bar = Bar('Processing', max=chainLength)
    for m_compt in list(range(chainLength)):
        #for loop

        #updating the abundance coefficients

        abundanceSamples, rhoSamples = sampleAbund.generateSamples(abundanceSamples, sigma2rSamples, rhoSamples,
         							imagePixel.SpectralValues, imagePixel.EndmembersMatrix, m_compt)
        #abundanceSamples.CurrentSamples = np.array([[0.3], [0.7]])
        TAlphaPlus.FillIn(abundanceSamples, m_compt)
        TRho.FillIn(rhoSamples, m_compt)

        if (m_compt > 0) and (np.fmod(m_compt, 100) == 0):
        	# abundance vector acceptance rate for every 100 iterations
        	vecRhoSamples = TRho.getNSamples(100,m_compt - 99)
        	sampleAbund.Tx = np.reshape(np.mean(vecRhoSamples, axis=1), (imagePixel.EndmembersNumber,1))

        #updating the variance
        sigma2rSamples = sampleVar.generateSamples(sigma2rSamples, abundanceSamples,
        				imagePixel.SpectralValues, imagePixel.EndmembersMatrix, delta)
        #sigma2rSamples.CurrentSamples = np.array([[0.001, 0.001]])
        TSigma2r.FillIn(sigma2rSamples, m_compt)

        #updating hyperparameter
        delta = sampleDelta.generateSamples(sigma2rSamples)

        bar.next()

    #end of loop
    bar.finish()
    return TAlphaPlus, TSigma2r






