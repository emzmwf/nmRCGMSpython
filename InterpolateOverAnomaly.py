#  Python script to extrapolate over anomoly in plot e.g. measured drift

# imports
import DigitalMicrograph as DM
import numpy as np
import sys
sys.argv.extend(['-a', ' '])
import matplotlib.pyplot as plt

print("/n ======== /n")

# Select the plot
image_0 = DM.GetFrontImage()
im_name = image_0.GetName()

NumArr = image_0.GetNumArray() # Get NumpyArray to image data

#nDim = image_0.GetNumDimensions()
#numpy_array = image_0.GetNumArray()*image_0.GetIntensityScale() 
#i_unit = image_0.GetIntensityUnitString()	# get y axis units
#i_origin = image_0.GetIntensityOrigin()	# y axis origin


# Get the anomoly range from selected area
# get range?
# val, val2= roi.GetRange()

# Or just ask the user
# Prompt the user for positions
ok, SPos = DM.GetNumber( 'Enter index to start interpolation over.', 30 ) 
ok, EPos = DM.GetNumber( 'Enter index to end interpolation over.', 50 )

#spectrumBefore = NumArr[int(0),int(SPos)]
#spectrumAnomoly = NumArr[int(SPos),int(EPos)]
spectrumOut = NumArr[:,:]

#spectrumBefore = NumArr[(NumArr>=1)*(NumArr<33)] # no, this is values
spectrumBefore = NumArr[:, 0:int(SPos-1)]
#spectrumBefore = NumArr[0:int(SPos-1), 0:int(SPos-1)]
spectrumDuring = NumArr[:, int(SPos):int(EPos)]
#spectrumDuring = NumArr[int(SPos):int(EPos), int(SPos):int(EPos)]

#so the width is the NumArr.size / length
MaxIndex = NumArr.size / len(NumArr)
print("Max index is ")
print(MaxIndex)

#SPEC1 = DM.CreateImage(spectrumBefore.copy(order='C')).ShowImage()
#testImg = DM.GetFrontImage()
#testImg.SetName("Before")
#img_disp = testImg.GetImageDisplay(0)
#img_disp.ChangeDisplayType(3)   #1 is image, 2 is 3d plot, 3 is a line plot

#SPEC2 = DM.CreateImage(spectrumDuring.copy(order='C')).ShowImage()
#testImg2 = DM.GetFrontImage()
#testImg2.SetName("During")
#img_disp2 = testImg2.GetImageDisplay(0)
#img_disp2.ChangeDisplayType(3)   #1 is image, 2 is 3d plot, 3 is a line plot

#print(spectrumDuring)
#print(spectrumDuring.shape)    # get array shape, should be 2 by number of inxed points
#print(spectrumDuring[:,1])  # give values of second index point (zero is first)
#print(spectrumDuring[1,:])  # gives values of y axis shift, x shift is first array

#a = np.array([[1, 2, 3], [3, 4, 5]])
#b = np.array([[5, 6], [6, 8]])
#specOut = np.concatenate((a,b), axis=1)
#print(specOut)

spectrumAft = np.zeros([2,1])
#spectrumAft = np.array([])

#Check if there is any after
IsAft = 0
if (EPos < MaxIndex):
    print("There is an after")
    IsAft = 1
    spectrumAft = NumArr[:, int(EPos+1):int(MaxIndex)]
#    SPEC3 = DM.CreateImage(spectrumAft.copy(order='C')).ShowImage()
#    testImg3 = DM.GetFrontImage()
#    testImg3.SetName("After")
#    img_disp3 = testImg3.GetImageDisplay(0)
#    img_disp3.ChangeDisplayType(3)   #1 is image, 2 is 3d plot, 3 is a line plot
    

print("spectrum after size")
print(spectrumAft.size)

#Set to Zero or interpolate?
#Choice = "zero"
Choice = "int"


# def - remove anomoly set to zero
def anomolyzero(spectrumAnomoly):
    spectrumAnomoly[abs(spectrumAnomoly) > 50] = 0
    return(spectrumAnomoly)

# def - remove anomoly, interpolate
def anomolyinterpolate(specA, specB, **kwargs):
    AL = specA.shape[1]
    BL = specB.shape[1]
    specC = kwargs.pop('specC', '')
    print("specC size is ")
    print(type(specC))
            
    #optional specC will be a string unless it is defined
    if type(specC)== str:
        if Choice == "zero":
            print("choice is to zero")
            specB[abs(specB) > 50] = 0
        else:
            print("choise is interpolate")
            #get the last values from specA
            #length of the array is specA.shape[1]
            #need AL-1 index
            fxval = specA[0][AL-1]
            fyval = specA[1][AL-1]
            #print(fxval)
            #print(fyval)
            specB[0,:] = fxval
            specB[1,:] = fyval
            #specB.fill(fxval)
        specOut = np.concatenate((specA,specB), axis=1)
    else:
        if Choice == "zero":
            print("choice is to zero")
            specB[abs(specB) > 50] = 0
        if Choice == "int":
            print("choice is to interpolate")
            #get the last values from specA
            #and the first values from specC
            #length of the array is specA.shape[1]
            #need AL-1 index
            fxvalA = specA[0][AL-1]
            fyvalA = specA[1][AL-1]
            fxvalC = specC[0][0]
            fyvalC = specC[1][0]
            #Probably want to use scipy to interpolate this later, for now just quick and dirty
            CL = specC.shape[1]
            for i in range(CL-1):
                fxval = (fxvalA*(1-(i/CL))+fxvalC*(i/CL))
                specB[0,i] = fxval
                fyval = (fyvalA*(1-(i/CL))+fyvalC*(i/CL))
                specB[1,i] = fyval
         
            specOut = np.concatenate((specA,specB, specC), axis=1)
    return (specOut)
#
#Run the DEF of choice

if (EPos < MaxIndex):
    specOut = anomolyinterpolate(spectrumBefore, spectrumDuring, specC = spectrumAft)
else:
    specOut = anomolyinterpolate(spectrumBefore, spectrumDuring)

SPEC3 = DM.CreateImage(specOut.copy(order='C')).ShowImage()
testImg3 = DM.GetFrontImage()
testImg3.SetName("Int")
img_disp3 = testImg3.GetImageDisplay(0)
img_disp3.ChangeDisplayType(3)   #1 is image, 2 is 3d plot, 3 is a line plot



#spectrumDuring = anomolyzero(spectrumDuring)



#b = 0
#if IsAft > b:
#  specOut = np.concatenate((spectrumBefore,spectrumDuring, spectrumAft), axis=1)
#else:
#  specOut = np.concatenate((spectrumBefore,spectrumDuring), axis=1)

image_0.UpdateImage()