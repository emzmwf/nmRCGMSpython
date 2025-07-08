import DigitalMicrograph as DM
import numpy as np

import sys
sys.argv.extend(['-a', ' '])

import matplotlib.pyplot as plt

# Get from image assuming EELS spectrum selected

image_0 = DM.GetFrontImage()
im_name = image_0.GetName()
nDim = image_0.GetNumDimensions()
numpy_array = image_0.GetNumArray()*image_0.GetIntensityScale() 
i_unit = image_0.GetIntensityUnitString()	# get y axis units
i_origin = image_0.GetIntensityOrigin()	# y axis origin

# Get x axis calibration and units
originX, scaleX, unitX =  image_0.GetDimensionCalibration(0, 0)
print(scaleX)
print(originX)

# get length of array
t = numpy_array[0]
tl = len(t)
print("\n t length is "+str(tl))

#get xdata
xdata = np.copy(numpy_array)
ydata = np.copy(numpy_array)

#fill the xdata array

#for i in ydata:
for i in range(0, tl):
    #Offset         originX
    #X per channel  scaleX
    #eV is (pixel*scale)+offset
    xdata[0][i] = (i*scaleX)+originX
    continue

print("\n xdata")
print(xdata)
print("\n ydata")
print(ydata)

xscaled = xdata

plt.plot(xscaled[0],ydata[0]) 

plt.xlabel(unitX)
plt.ylabel(i_unit)

#Style list
#['default', 'classic', 'Solarize_Light2', '_classic_test_patch', 'bmh', 'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn', 'seaborn-bright', 'seaborn-colorblind', 'seaborn-dark', 'seaborn-dark-palette', 'seaborn-darkgrid', 'seaborn-deep', 'seaborn-muted', 'seaborn-notebook', 'seaborn-paper', 'seaborn-pastel', 'seaborn-poster', 'seaborn-talk', 'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid', 'tableau-colorblind10']

plt.style.use('seaborn-colorblind')


print('Start plotting. Script continues when figure is closed')
plt.show()
print("Figure will appear in separate window as matplot format")

# clean up memory
del(numpy_array)
del(xdata)
del(ydata)
del(xscaled)
del(image_0)
