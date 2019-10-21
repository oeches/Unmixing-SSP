This package contains programs that have been written by O. ECHES, N. DOBIGEON and J.-Y. TOURNERET, for the
implementation of the hyperspectral linear unmixing procedure for the Normal Compositional Model. For more details:

O. Eches, N. Dobigeon, C. Mailhes and J.-Y. Tourneret, "Unmixing hyperspectral images 
using a Normal Compositional Model and MCMC methods," in Proc. IEEE Workshop on Statistical 
Signal Processing (SSP), Cardiff, Wales, UK, 2009, pp.646-649.

The function "unmixing.py" calls the different sampler that are defined in the modelMCMC class.
You can edit this file to understand the structure of the procedure based on a hierarchical model
and a Gibbs sampling strategy.
The programs are written in Python3.
You will find in "example_unmixing.py" the main function to execute, a code which allows you 
to perform the unmixing procedure on a synthetic pixel with parameters you can freely define:
- number of endmembers in the pixel
- spectral library file (in .npy format) 
- number of MCMC samples and burn-in iterations
- sampling step for the spectal library
- variance of the noise
Then, the abundances are randomly automatically generated. It is possible to give a random seed
at the beginning of the function. Up to 6 endmembers may be tested on a given pixel.

The package required are given in the requirements.txt file.
On UNIX systems, simply launch "python3 example_unmixing.py" in the correct folder.

The files come along with class and .npy files for the analysis of a real image.
Unfortunately, due to the lack of computational resources, it has not been tested yet.
Feel free to manipulate the different functions to test the algorithm on a real image !

If you have any question on the code : olivier.eches@gmail.com