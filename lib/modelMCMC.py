#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Class MCMCChains, Samples and SamplerMCMC"""
import numpy as np

class MCMCChains:
    """Class that creates and fill the MCMC samples generated by the distributions"""
    def __init__(self, length, dimension, name):
        """Initialization of the chains (please vectorize any matrix)"""
        self.length = length
        self.SampleValues = np.empty([dimension, length])
        self.name = name # name of the chain

    def FillInitialSamples(self, samplesInit):
        """Fill in the chains with the initial samples"""
        self.SampleValues[:,0] = np.ravel(samplesInit)

    def FillIn(self, samples, index):
        """Fill in the chains with the samples"""
        self.SampleValues[:,index] = np.ravel(samples.CurrentSamples)

    def getNSamples(self, Nsamples, Nbegin):
    	"""Get the Nsamples from the Nbeginth sample"""
    	listSamples = self.SampleValues[:,Nbegin:(Nsamples+Nbegin)]
    	return listSamples

class Samples:
    """Class that will be used to store the current and previous generated samples"""
    def __init__(self, dimension, Name, sampleInit):
        """Initialization of the samples"""
        self.dimension = dimension
        self._PreviousSamples = np.empty([dimension, 1])
        self._CurrentSamples = sampleInit
        self.Name = Name

    @property
    def PreviousSamples(self):
        """Getter for previous Sample"""
        return self._PreviousSamples

    @PreviousSamples.setter
    def PreviousSamples(self, sampleValue):
        """Setter for previous Sample"""
        self._PreviousSamples = sampleValue

    @property
    def CurrentSamples(self):
        """Getter for current Sample"""
        return self._CurrentSamples

    @CurrentSamples.setter
    def CurrentSamples(self, sampleValue):
        """Setter for current Sample"""
        self._CurrentSamples = sampleValue

class SamplerMCMC:
    """Abstract class that will generate the samples"""
    def __init__(self):
        """Class initialization"""

    def generateSamples(self, samples):
        """Virtual method that generate samples"""
        raise NotImplementedError

class MetropolisWithinGibbs(SamplerMCMC):
    """Sub class of Sampler MCMC that do a Metropolis within Gibbs algorithm"""
    def __init__(self, acceptanceProbability):
        """Initialization, set of acceptanceProbability"""
        super().__init__()
        self.acceptProbability = acceptanceProbability

    def generateSamples(self, samples):
        """Virtual method that generate samples"""
        raise NotImplementedError

class MwG_abundances(MetropolisWithinGibbs):
    """Sub class of MetropolisWithinGibbs that generate the abundances"""
    def __init__(self, Tx, varRandomWalk, acceptProb):
        """Initialize the sampler"""
        super().__init__(acceptProb)
        self._Tx = Tx
        self._varRandomWalk = varRandomWalk

    @property
    def Tx(self):
        """Getter for acceptation rate"""
        return self._Tx
    
    @Tx.setter
    def Tx(self, TxVal):
        """Setter for acceptation rate"""
        self._Tx = TxVal
    
    @property
    def varRandomWalk(self):
        """Getter for random walk variance"""
        return self._varRandomWalk
    
    @varRandomWalk.setter
    def varRandomWalk(self, varValue):
        """Setter for random walk variance"""
        self._varRandomWalk = varValue
    
    def generateSamples(self, samplesAb, samplesSig, samplesRho, data, spectra, index):
        """Sampler of abundances vector"""
        shapeSpectra = spectra.shape 
        bandsNumber = shapeSpectra[0]

        rho = samplesRho.CurrentSamples
        #rho = 0 if proposed sample rejected, rho = 1 else

        #selecting the first abundance coefficient to be sampled
        randPermut = np.random.permutation(samplesAb.dimension)

        firstAb = randPermut[0]
        listAbArr = np.setdiff1d(randPermut, firstAb)
        listAb = listAbArr.tolist()

        for k in listAb:
            ind_k = listAb.index(k)
            spectra_k = spectra[:, listAb]
            spectra_k = np.delete(spectra_k, ind_k, 1)
            Sk = samplesSig.CurrentSamples[:,listAb]
            Sk = np.delete(Sk, ind_k, 1)
            alpha_k = samplesAb.CurrentSamples[listAb]
            alpha_k = np.delete(alpha_k, ind_k, 0)
            if not alpha_k.size:
                alpha_k = 0.
                Sk = np.zeros((1,1))
                spectra_k = np.zeros((bandsNumber,1))

            # random walk

            # determining the Gaussian variance in function of the acceptance rate
            # every 100 iterations

            if ((self.Tx[k] > 0.4) and ((index-1) % 100 == 0)):
                self.varRandomWalk[0,k] *= 5
            elif ((self.Tx[k] < 0.3) and ((index-1) % 100 == 0)):
                self.varRandomWalk[0,k] /= 5

            # proposed samples
            alpha = samplesAb.CurrentSamples[k] + np.sqrt(self.varRandomWalk[0,k])*np.random.randn()

            if (alpha > 0) and (alpha < (1 - np.sum(alpha_k))):
                #alpha_star = np.asscalar(alpha) # deprecated
                alpha_star = alpha.item()
                
                mu_alpha = spectra[:,0:(samplesAb.dimension-1)].dot(samplesAb.CurrentSamples[0:(samplesAb.dimension-1)]) \
                +spectra[:,[samplesAb.dimension-1]].dot(1-np.sum(samplesAb.CurrentSamples[0:(samplesAb.dimension-1)]))
                C_alpha = samplesSig.CurrentSamples[:,0:(samplesAb.dimension-1)].dot(np.square(samplesAb.CurrentSamples[0:(samplesAb.dimension-1)])) \
                + samplesSig.CurrentSamples[:,samplesAb.dimension-1].dot(np.square(1 - np.sum(samplesAb.CurrentSamples[0:(samplesAb.dimension-1)])))
                mu_alpha_star = spectra[:,[k]]*alpha_star + spectra_k.dot(alpha_k) \
                + spectra[:,[firstAb]].dot(((1 - (alpha_star + np.sum(alpha_k)))))
                C_alpha_star = samplesSig.CurrentSamples[:,k].dot(np.square(alpha_star)) + Sk.dot(np.square(alpha_k))\
                + samplesSig.CurrentSamples[:,firstAb]*(np.square(1 - (alpha_star + np.sum(alpha_k))))

                # difference between the logarithms of the distributions
                varDiff = 0.5*(np.square(np.linalg.norm(data - mu_alpha_star))/C_alpha_star \
                - np.square(np.linalg.norm(data - mu_alpha))/C_alpha) \
                + (bandsNumber/2)*np.log(C_alpha_star/C_alpha)
            else:
                varDiff = np.inf

            # Acceptance-reject procedure to determine samplesAb(t+1)
            if (varDiff < 0) or (np.exp(-varDiff) > np.random.rand()):
                samplesAb.CurrentSamples[k] = alpha_star
                rho[:,k] = 1
            else:
                rho[:,k] = 0


        samplesAb.PreviousSamples = samplesAb.CurrentSamples
        samplesAb.CurrentSamples[firstAb] = 1 - np.sum(samplesAb.CurrentSamples[listAb])
        samplesRho.PreviousSamples = samplesRho.CurrentSamples
        rho[:,firstAb] = 0
        samplesRho.CurrentSamples = rho

        return samplesAb, samplesRho

class GibbsForVariance(SamplerMCMC):
    """Sub class for endmember variance generation """
    def __init__(self):
        """Initialize the sampler"""
        super().__init__()

    def generateSamples(self, samplesSig, samplesAb, data, spectra, delta):
        """Sampler (gibbs) of endmember variance"""
        sizeOfEndmember = np.shape(spectra)
        L = sizeOfEndmember[0]
        R = sizeOfEndmember[1]

        normOfModel = np.linalg.norm(data - spectra.dot(samplesAb.CurrentSamples))
        normOfModelSquare = np.square(normOfModel)
        B = normOfModelSquare/(2*np.sum(np.square(samplesAb.CurrentSamples))) + delta

        sig2inv = np.random.gamma(L/2+1, np.reciprocal(B))
        sig2inv = np.dot(sig2inv,np.ones((1,R)))

        samplesSig.CurrentSamples = np.reciprocal(sig2inv)
        
        return samplesSig


class GibbsForHyperparameter(SamplerMCMC):
    """Sub class for hyperparameter generation """
    def __init__(self):
        """Initialize the sampler"""
        super().__init__()

    def generateSamples(self, samplesSig):
        """Sampler (gibbs) of hyperparameter"""
        sig2 = samplesSig.CurrentSamples[:,0].item()

        delta = np.random.gamma(1, sig2)

        return delta



