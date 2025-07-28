# nmRCGMSpython

Python scripts for Gatan Microscopy Suite, used at the University of Nottingham nmRC

Primarily scripts written for GMS 3.61 and 3.62, used with OneView and K3 detectors, on JEOL 2100Plus and 2100F microscopes.


Each script is standalone, but may require some additional standard python packages to be installed above the base GMS python installation (e.g. SciPy). Gatan advice is to use Pip to install additional packages as conda may change the numpy environment. 


Project maintainer - Dr Mike Fay  


## BeamTiltReportZemlin.py
Python script to do something like a Zemin tableau
Temporarily adjusts bright tilt around a centre to show distortions and shows modulus of FFTs arranged in a new workspace
Checks if GMS has calibrated beam tilts, runs uncalibrated if not

## ColorTableFromMatplotlib.py
Script to export Matplotlib colour tables into images that can be saved as the dm3 format used for ColorTables in GMS

## EELSreplotAsMatplot.py
Takes front image (assuming a GMS EELS image) and replots into Matplot for figure generation purposes

## FFTArrayAnalysis.py
Turns HRTEM image into an FFT 4D Stack (uses functions from BenMiller at Gatan - requires Scipy, BenMillerScriptsScripts)

## ImportPNG.py
Imports png file into GMS 

## Importh5oina
Script to import data from the Oxford Instruments file format h5oina. This version is written to work with export from AZtec 6.1, so does not include import of spectra files. These would need to be seperately exported as .msa format to be loaded into GMS. 
Script will read pixel size data and add as calibration. Colourisation option uses look up tables to colourise, uses additional color tables from nmrC_DMScripts/ColorTables/

## InterpolateOverAnomaly
To extrapolate over an anomoly in a plot e.g. measured drift
