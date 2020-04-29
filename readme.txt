This package contains programs that have been written by O. ECHES, N. DOBIGEON and J.-Y. TOURNERET, for the
implementation of the hyperspectral linear unmixing procedure for the Normal Compositional Model. For more details:

O. Eches, N. Dobigeon, C. Mailhes and J.-Y. Tourneret, "Unmixing hyperspectral images 
using a Normal Compositional Model and MCMC methods," in Proc. IEEE Workshop on Statistical 
Signal Processing (SSP), Cardiff, Wales, UK, 2009, pp.646-649.

The function "unmixing.py" calls the different sampler that are defined in the modelMCMC class.
You can edit this file to understand the structure of the procedure based on a hierarchical model
and a Gibbs sampling strategy.
The programs are written in Python3.

The main program to call is "main.py" and will show you a small window where you can choose to unmix
either a real image or a synthetic pixel. Then a new window will appear with different options
for the synthetic pixel (spectral library, number of endmembers, abundance values, noise level). 
For a real image, you have to load the image data file (in .npy format) and the corresponding
spectral library file (also in .npy format).

The spectral library data file for synthetic or real image must contain a dictionary whose keys are
"Wavelength" (the wavelength number) and "spectra" (spectral values of each endmember for each wavelength number).
The values must be numpy array types.

The hyperspectral image data file must contain a dictionary whose keys are
"image" (the image values of each pixel) and "mask" (vector indicating the water absorption bands).
The values must be numpy array types. In particular, the "image" value field is a 2D-numpy array of
size equal to the image in pixels. The "mask" value is a 1D-numpy array of size equal to the number of 
bands and whose values are boolean (a "1" indicates the current band is NOT masked, "0" otherwise).

These dictionnary should be enclosed in numpy array (since it has .npy format).

For the synthetic pixel unmixing option, up to 6 endmembers may be tested on a given pixel.
After unmixing, a window appear giving mean value of the abundances and also the histograms
of the MCMC chains of these parameters.

It is also possible to launch a console application, "example_unmixing.py", a code which allows you 
to perform the unmixing procedure on a synthetic pixel with parameters you can freely define at hand:
- number of endmembers in the pixel
- spectral library file (in .npy format) 
- number of MCMC samples and burn-in iterations
- sampling step for the spectal library
- variance of the noise
Then, the abundances are randomly automatically generated. It is possible to give a random seed
at the beginning of the function. Up to 6 endmembers may be tested on a given pixel.

The package required are given in the requirements.txt file.
On UNIX systems, simply launch "python3 main.py" in the correct folder.

The files come along with class and .npy files for the analysis of a real image. You cand find them in the
data folder. 
Feel free to use these files as example : 
- spectraSynth_dict.npy for the spectral library file for a synthetic pixel
- imageROIMoffet.npy for the image file for unmixing of a real image
- spectraMoffetROI_dict.npy for the spectral library file associated with the given image file

If you have any question on the code : olivier.eches@gmail.com