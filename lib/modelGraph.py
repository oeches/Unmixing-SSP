#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Class Graph to display"""
import numpy as np
#import matplotlib as mil
#mil.use('TkAgg')
import matplotlib.pyplot as plt

class GraphBase():
    """Class for graph (mother class)"""
    def __init__(self):
        """Initialization of base graph"""
        self.title = "Your graph title"
        self.x_label = "X-axis label"
        self.y_label = "Y-axis label"
        #self.fighandle = plt.figure(number)

    def show(self, x_values, y_values):
        """Method that display the graph"""
        # x_values = gather only x_values from our zones
        # y_values = gather only y_values from our zones
        #x_values, y_values = self.xy_values(zones)
        plt.plot(x_values, y_values, '.')
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title)
        plt.show()

    def xy_values(self, zones):
        raise NotImplementedError

class HistogramSamples(GraphBase):
    """Display of MCMC samples histograms"""

    def __init__(self, number, Nclass):
        """Initialization of histograms"""
        super().__init__()
        self.title = "Posterior distribution of MCMC samples"
        self.x_label = "Samples values"
        self.y_label = "Posterior distribution"
        self.Nclass = Nclass
        self.fignumber = number

    def compute(self, Nmc, Nbi, Samples, name, sizeToDisplay):
        """Posterior distribution of the samples"""
        # Number of histograms to show depends of the sizeToDisplay
        #import pdb; pdb.set_trace()
        fighandle = plt.figure(self.fignumber)
        TSamplesR = Samples.getNSamples(Nmc-Nbi+1,Nbi)
        meanOfSamples = np.zeros((sizeToDisplay,1))
        for indR in list(range(sizeToDisplay)):
            Tsamples = TSamplesR[indR, :]
            xmin = (0.8*np.amin(Tsamples))
            xmax = (1.2*np.amax(Tsamples))
            self.Nclass = np.int_(np.sqrt(Nmc - Nbi + 1))
            hist_norm = np.histogram(Tsamples, bins=self.Nclass, range=(xmin, xmax), density=True)
            if (sizeToDisplay > 1):
                if (sizeToDisplay > 3):
                    plt.subplot(2,3,indR+1)
                else:
                    plt.subplot(1,3,indR+1)
            plt.plot(np.linspace(xmin,xmax,self.Nclass),hist_norm[0])
            meanOfSamples[indR] = np.mean(Tsamples)
            if (sizeToDisplay > 1):
                self.title = ["{}_{}".format(name, indR+1)]
                #compute mean value
                print("mean val_{} = {}".format(indR+1, meanOfSamples[indR]))
            else:
                self.title = ["Posterior distribution of {}".format(name)]
                #compute mean value
                print("mean val = {}".format(meanOfSamples[indR]))

            plt.title(self.title)
            plt.xlabel(self.x_label)
            plt.ylabel(self.y_label)

        return meanOfSamples, fighandle

class AbundanceMaps():
    """Display of abundance maps obtained for a given image"""

    def __init__(self, NumMaps, sizeX, sizeY):
        """Initialization of maps"""
        self.NumMaps = NumMaps
        self.sizeX = sizeX
        self.sizeY = sizeY

    def show(self, MeanAbund):
        """Display of maps"""
        for indR in list(range(self.NumMaps)):
            # reshaping data
            meanA = MeanAbund[indR, :]
            AlphaImage = np.reshape(meanA, (self.sizeY, self.sizeX))
            AlphaImage = np.round(255*AlphaImage)
            #fig, ax = plt.subplots()
            if (self.NumMaps > 1):
                if (self.NumMaps > 3):
                    plt.subplot(2,3,indR+1)
                else:
                    plt.subplot(1,3,indR+1)
            plt.imshow(AlphaImage, aspect = 'equal')

            title = ["Abundance of endmember {}".format(indR+1)]
        
        plt.show()

