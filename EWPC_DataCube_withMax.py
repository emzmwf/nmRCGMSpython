# EWPC a full datacube

# Note, for larger datasets, best to divide into sections first, 
# this script cannot handle 16Gb datasets currently
#100x100x256x256 takes 

# Works VERY BADLY with a beam stop 

import skimage
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft2, fftshift
import DigitalMicrograph as DM


##########################
# DEFs 
##########################


#
def Tag_Copy(image_source, image_dest, subPath = None ):
### Main body of script ###
 '''
 Copy all tags between source and destination.
 If no destination subPath is provided, the destination tags will be replaced.
 '''
 #Copy Tags
 tg_source = image_source.GetTagGroup()
 tg_dest = image_dest.GetTagGroup()
 if ( subPath != None ):
         tg_dest.SetTagAsTagGroup(subPath,tg_source.Clone())
 else:
         tg_dest.DeleteAllTags()
         tg_dest.CopyTagsFrom(tg_source.Clone())

#
#Tag_Copy(image_4D, newimage_4D)
# This command currently makes the dataset act weirdly in GMS 


def Tag_CopySelective(image_4D, newimage_4D):
    tg_source = image_4D.GetTagGroup()
    tg_dest = newimage_4D.GetTagGroup()
    MIval = tg_source.GetTagAsTagGroup('Microscope Info')
    #window = MIval.OpenBrowserWindow(True) 
    
    tg_dest.SetTagAsTagGroup('Microscope Info', MIval) 
    
    tg_dest.SetTagAsTagGroup('Acquisition', tg_source.GetTagAsTagGroup('Acquisition')) 
    tg_dest.SetTagAsTagGroup('Calibration', tg_source.GetTagAsTagGroup('Calibration')) # If enabled, SI signal doesn't work
    #tg_dest.SetTagAsTagGroup('Data Bar', tg_source.GetTagAsTagGroup('Data Bar')) 
    tg_dest.SetTagAsTagGroup('Diffraction', tg_source.GetTagAsTagGroup('Diffraction')) 
    tg_dest.SetTagAsTagGroup('DigiScan', tg_source.GetTagAsTagGroup('DigiScan')) 
    tg_dest.SetTagAsTagGroup('Meta Data', tg_source.GetTagAsTagGroup('Meta Data')) 
    tg_dest.SetTagAsTagGroup('SI', tg_source.GetTagAsTagGroup('SI'))
    #tg_dest.SetTagAsTagGroup('Parent', tg_source.GetTagAsTagGroup('Parent'))  
    #tg_dest.SetTagAsTagGroup('Processing', tg_source.GetTagAsTagGroup('Processing'))  
    #tg_dest.SetTagAsTagGroup('Session Info', tg_source.GetTagAsTagGroup('Session Info'))  
    tg_dest.SetTagAsBoolean('Meta Data:Data Order Swapped', False) 
    


def DoEWPC(dmImgData):
    image = dmImgData.astype("float32")
    
    image = image*100
    image = image+1

    Xsize = image.shape[0]
    Ysize = image.shape[1]

    #TODO- check X and Y size are the same, crop if not
    #TODO- check there are no zero or lower values
    
    # Make Hann filter
    win = skimage.filters.window('hann', (Xsize, Ysize))
    
    #Process image
    
    logimage = np.log(image)    #Get log of image
    wimage = logimage * win     #Apply Hann filter
    wimage_f = np.abs(fftshift(fft2(wimage)))   #Get fft
    return wimage_f

def GetXYMax(im_arr):
    innerval = 8 # no of pixels radius from centre to start looking for max
    outerval = 12 # no of pixels radius from centre to look for the outer max
    C, D = np.shape(im_arr)
    MaxVal = 0
    MaxVal2 = 0
    XMax = 0
    YMax = 0
    XMax_O = 0
    YMax_O = 0

    for i in range(C):
        for j in range(D):
            compA = i-int(C/2)
            compB = j-int(D/2)
            rval = abs(compA*compA+compB*compB)
            if (rval > (innerval*innerval)):
                tval = im_arr[i,j]
                if (tval > MaxVal):
                    MaxVal = tval
                    XMax = i
                    YMax = j
            if (rval > (outerval*outerval)):
                tval = im_arr[i,j]
                if (tval > MaxVal2):
                    MaxVal_O = tval
                    XMax_O = i
                    YMax_O = j
    print(MaxVal)
    return XMax, YMax, MaxVal, XMax_O, YMax_O, MaxVal_O
    
def DoDatacube(raw_datacube, name, order):
    print (np.shape(raw_datacube))
    A,B,C,D = np.shape(raw_datacube)
    #Am expecting A and B to be the image dimension, C and D to be the diffraction dimensions

    #Process Dataset
    #Set up new data set
    newdata = np.copy(raw_datacube)
    if (np.min(newdata)<=1):
        newdata = newdata + 1 + np.abs(np.min(newdata))
        
    #Make array for maximums
    maxarr = np.full((6, A, B), 0)
    
    #set region of beam stop to NAN
    # Three lines identified by y = Ax + B threshold value
    # line 1: y is less than threshold (below)
    # line 2: y is above threshold (to right of line)
    # line 3: y is below threshold (to left of line)
    # 
    
    
    
    #Iterate through dataset to make EWPC of each DP
    for i in range(A):
        for j in range(B):
            DP = newdata[i,j,:,:]
            EWPC = DoEWPC(DP)
            # Get X_Max, Y_Max
            XMax, YMax, ValMax, XMax_O, YMax_O, ValMax_O = GetXYMax(EWPC)
            # Add these to MaxArray 
            maxarr[0, i, j] = XMax
            maxarr[1, i, j] = YMax
            maxarr[2, i, j] = ValMax
            maxarr[3, i, j] = XMax_O
            maxarr[4, i, j] = YMax_O
            maxarr[5, i, j] = ValMax_O
            newdata[i,j,:,:] = EWPC

    
    if (order == 2):
        newdata_tp = np.transpose(newdata, (2,3,0,1))
    if (order == 1):
        newdata_tp = np.transpose(newdata, (0,1,2,3))# Puts diffraction pattern first and image in SI?
    #newdata_tp = np.copy(newdata)

    image_4D = DM.GetFrontImage()

    #Show XMax
    image_XMax = DM.CreateImage(np.copy(maxarr[0,:,:]))
    image_XMax.SetName("X Maximum")
    image_XMax.ShowImage()

    #Show XMax_O
    image_XMax_O = DM.CreateImage(np.copy(maxarr[3,:,:]))
    image_XMax_O.SetName("X Outer Maximum")
    image_XMax_O.ShowImage()

    
    #Show YMax
    image_YMax = DM.CreateImage(np.copy(maxarr[1,:,:]))
    image_YMax.SetName("Y Maximum")
    image_YMax.ShowImage()

    #Show XMax_O
    image_XMax_O = DM.CreateImage(np.copy(maxarr[4,:,:]))
    image_XMax_O.SetName("Y Outer Maximum")
    image_XMax_O.ShowImage()

    
    #Show MaxVal
    image_ValMax = DM.CreateImage(np.copy(maxarr[2,:,:]))
    image_ValMax.SetName("MaximumValue")
    image_ValMax.ShowImage()
    
    #Show MaxVal
    image_ValMax_O = DM.CreateImage(np.copy(maxarr[5,:,:]))
    image_ValMax_O.SetName("MaximumValue")
    image_ValMax_O.ShowImage()


    #Show new 4D dataset last
    d_im = DM.CreateImage(np.copy(newdata_tp, order ='c'))
    print (np.shape(d_im))
    d_im.ShowImage()
    d_im.SetName("EWPC datacube")
    
    Tag_CopySelective(image_4D, d_im)
    

def Main():
    import time
    start_time = time.time()

    image_4D = DM.GetFrontImage()
    if image_4D.GetNumDimensions() != 4: DM.OkDialog("Front-Most Image is not a 4D Dataset...\n\nAborting Script") ; exit()
    raw_datacube = image_4D.GetNumArray()
    name = image_4D.GetName()
    origin, x_scale, scale_unit =  image_4D.GetDimensionCalibration(0, 0)

    print(image_4D.GetDimensionScale(0))
    #print(image_4D.GetDimensionScale(1))
    #print(image_4D.GetDimensionScale(2))
    #print(image_4D.GetDimensionScale(3))
    sizex = image_4D.GetDimensionSize(0)
    sizey = image_4D.GetDimensionSize(1)
    sizej = image_4D.GetDimensionSize(2)
    sizek = image_4D.GetDimensionSize(3)

    order = 2

    DoDatacube(raw_datacube, name, order)

    DM.OkDialog( 'Datacube processed' ) 

    newimage_4D = DM.GetFrontImage()


    if (order == 2):
        ScaleA = image_4D.GetDimensionScale(2)
        ScaleB = image_4D.GetDimensionScale(0)
        unitA = image_4D.GetDimensionUnitString(2)
        unitB = image_4D.GetDimensionUnitString(0)
        if (ScaleA == "b'\xb5m'"):
            ScaleA = "nm"
            unitA = unitA*1000
        newimage_4D.SetDimensionUnitString(0, str(unitA))
        newimage_4D.SetDimensionUnitString(1, str(unitA))
        newimage_4D.SetDimensionUnitString(2, str(unitB))
        newimage_4D.SetDimensionUnitString(3, str(unitB))
        newimage_4D.SetDimensionScale(0, ScaleA)
        newimage_4D.SetDimensionScale(1, ScaleA)
        newimage_4D.SetDimensionScale(2, ScaleB)
        newimage_4D.SetDimensionScale(3, ScaleB)
        print("Scale A is "+str(ScaleA))
        print(unitA)
        print(ScaleB)
        print(unitB)


    if (order == 1):
        ScaleA = image_4D.GetDimensionScale(0)
        ScaleB = image_4D.GetDimensionScale(2)
        unitA = image_4D.GetDimensionUnitString(0)
        unitB = image_4D.GetDimensionUnitString(2)
        if (ScaleA == "b'\xb5m'"):
            ScaleA = "nm"
            unitA = unitA*1000
        newimage_4D.SetDimensionUnitString(0, str(unitA))
        newimage_4D.SetDimensionUnitString(1, str(unitA))
        newimage_4D.SetDimensionUnitString(2, str(unitB))
        newimage_4D.SetDimensionUnitString(3, str(unitB))
        newimage_4D.SetDimensionScale(0, ScaleA)
        newimage_4D.SetDimensionScale(1, ScaleA)
        newimage_4D.SetDimensionScale(2, ScaleB)
        newimage_4D.SetDimensionScale(3, ScaleB)
        print("Scale A is "+str(ScaleA))
        print(unitA)
        print(ScaleB)
        print(unitB)

    del raw_datacube

    print("--- %s seconds ---" % (time.time() - start_time))
    
    
Main()