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

NumArr = np.copy(image_0.GetNumArray()) # Get NumpyArray to image data

# Or just ask the user
# Prompt the user for positions
ok, SPos = DM.GetNumber( 'Enter index to start interpolation over.', 30 ) 
ok, EPos = DM.GetNumber( 'Enter index to end interpolation over.', 50 )

spectrumOut = NumArr[:,:]

spectrumBefore = NumArr[:, 0:int(SPos-1)]
spectrumDuring = NumArr[:, int(SPos):int(EPos)]

#so the width is the NumArr.size / length
MaxIndex = NumArr.size / len(NumArr)
print("Max index is ")
print(MaxIndex)

spectrumAft = np.zeros([2,1])

#Check if there is any after
IsAft = 0
if (EPos < MaxIndex):
    print("End isn't the last point")
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
            specB[0,:] = fxval
            specB[1,:] = fyval
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
            print(np.shape(specB))
            print(CL)
            #for i in range(CL):
            for i in range(np.shape(specB)[1]):
                fxval = (fxvalA*(1-(i/CL))+fxvalC*(i/CL))
                print("i is "+str(i))
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

testImg3.SetName(im_name+"_Interpolated")
img_disp3 = testImg3.GetImageDisplay(0)
img_disp3.ChangeDisplayType(3)   #1 is image, 2 is 3d plot, 3 is a line plot

image_0.UpdateImage()
