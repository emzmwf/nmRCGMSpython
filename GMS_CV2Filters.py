'''

# Demo of OpenCV scripts within Gatan Digital Micrograph
# last updated November 2024 - package checking - MWF
# Convolution, Blur, Median Blur, Gaussian Blur, Bilateral, Wiener
#
# Filtered images have the same tags and calibration as the original
# file

# 0.6 - processing information added to tags
# 0.6 - correction to calibration copy to avoid issue with GMS 3.62

'''

import DigitalMicrograph as DM
import numpy as np

import sys

# Import non-standard packages with error catching
try:
    import cv2
except ModuleNotFoundError:
    print("\n module 'opencv-python' is not installed")
    print("note, install with pip install opencv-python, do not use conda")
    print("Ending script now")
    sys.exit(1) #exits noting an error


try:
    import scipy
except ModuleNotFoundError:
    print("\n module 'SciPy' is not installed")
    print("note, install with pip install scipy, do not use conda")
    print("Ending script now")
    sys.exit(1) #exits noting an error
#

# defs to copy the calibration data from the original to the new dm file
def Calibration_Copy(image_source, image_dest):
 '''
 Copy dimension and intensity calibration between source and destination.
 On mismatch of number of dimension, prompt user and return.
 '''
 #Count and check that number of dimensions match
 num_dim_s = image_source.GetNumDimensions()
 num_dim_d = image_dest.GetNumDimensions()
 if num_dim_d != num_dim_s:
         DM.OkDialog('Images do not have same number of dimensions!')
         return 
         
 #Copy Dimension Calibrations
 origin = [0 for _ in range(num_dim_s)]
 scale = origin
 power = origin
 unit = ["" for _ in range(num_dim_s)]
 unit2 = unit
 for i in range(num_dim_s):
         origin[i], scale[i], unit[i] =  image_source.GetDimensionCalibration(i, 0)
         #image_dest.SetDimensionCalibration(i,origin[i],scale[i],unit[i],0)
         unit2[i], power[i] = image_source.GetDimensionUnitInfo(i)
         image_dest.SetDimensionUnitInfo(i,unit2[i],power[i])
         ScaleA = image_source.GetDimensionScale(0)
         ScaleB = image_source.GetDimensionScale(1)
         image_dest.SetDimensionScale(0,ScaleA)
         image_dest.SetDimensionScale(1,ScaleB)
 
 #Copy Intensity Calibrations
 i_scale = image_source.GetIntensityScale()
 i_unit = image_source.GetIntensityUnitString()
 i_origin = image_source.GetIntensityOrigin()
 image_dest.SetIntensityScale(i_scale)
 image_dest.SetIntensityUnitString(i_unit)
 image_dest.SetIntensityOrigin(i_origin)
#
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
 

### def to move the newly displayed image to wsIDF
def CV2ImgMove(wsFilt):
    imageDocA = DM.GetFrontImageDocument()
    imageDocA.MoveToWorkspace(int(wsFilt))

# Add Processing info to tags
def TagProcessing(img_dest, proc_text):
    tg_dest = img_dest.GetTagGroup()
    tagpath = "Processing Tags:Processing"
    success, val = tg_dest.GetTagAsString(tagpath)
    if (success):
        #print("appending to processing list")
        val = val+","+proc_text
        tg_dest.SetTagAsString('Processing Tags:Processing', val)
    else:
        #print("No previous processing")
        procTG = DM.NewTagGroup()
        procTG.SetTagAsString('Processing', proc_text)
        tg_dest.SetTagAsTagGroup('Processing Tags', procTG)
    # check if processing tag list exists
    # count the number of existing tags
    # copy these and add new tag to end of processing list


def DoFilter(d):

    # Process the front image
    dmImg = DM.GetFrontImage() # Get reference to front most image
    dmImgData = dmImg.GetNumArray() # Get NumpyArray to image data
    
    #Get the image document and its window
    imageDoc = DM.GetFrontImageDocument()
    imDocWin = imageDoc.GetWindow()
    
    # Check if the front image is a stack
    nDim = dmImg.GetNumDimensions()
    # get the visible slice if so
    if (nDim==3):
        print("three dimensions found")
        DM.OkDialog("Script not currently compatible with stacks")
        exit()
        
    
    
    #print(dmImgData.dtype)
    #DM4 file is wrong format for cv2 so need to convert to float32
    result = dmImgData.astype("float32")
    
    # Apply Convolution
    kernel = np.ones((d,d),np.float32)/(d*d)
    Conv = cv2.filter2D(result,-1,kernel)
    
    # Apply Blur
    blur = cv2.blur(result,(d,d))
    
    #Apply Median Blur
    #If the input type is not np.uint8, the only allowed ksize values for cv2.medianBlur are 3 and 5.
    # so loop for (d/5) times instead?
    median_blur = cv2.medianBlur(result, 5)
    lno = int(d/5)
    for x in range(2, lno):
        median_blur = cv2.medianBlur(median_blur, 5)
    
    # Apply Gaussian
    Gaus = cv2.GaussianBlur(result,(d,d),0)
    
    # Apply Wiener filter - added May 2024
    from scipy.signal import wiener
    wien = wiener(result, (d, d))  #Filter the image

    # Apply Bilateral - may not do anything if edges aren't sharp?
    #bil = cv2.bilateralFilter(result,d,75,75)
    bil = cv2.bilateralFilter(result,d,75,75)
    
    # from python we can get the original workspace 
    # that has the front image document
    # find out what workspace that is in
    wsID = imageDoc.GetWorkspace() 
    
    # Make new workspace - the dm script version of this would be
    #number wsID_src = WorkSpaceGetActive()
    #number wsID_Filter = WorkSpaceAdd( WorkSpaceGetIndex(wsID_src) + 1 )
    #WorkSpaceSetActive( wsID_Filter )
    #WorkspaceSetName( wsID_Filter , "Filered" )
    # and use a temporary tag to pass the id number to python
    
    dmscript = 'number wsID_src = WorkSpaceGetActive()' + '\n'
    dmscript += 'number wsID_Filter = WorkSpaceAdd( WorkSpaceGetIndex(wsID_src) + 1 )' + '\n'
    dmscript += 'WorkspaceSetName( wsID_Filter , "Filtered '+str(d)+'" )' + '\n'
    dmscript += 'TagGroup tg = GetPersistentTagGroup( ) ' + '\n'
    dmscript += 'tg.TagGroupSetTagAsString( "DM2Python CV2", ""+wsID_Filter )' + '\n'
    
    DM.ExecuteScriptString( dmscript ) 
    # Now get the wsID_Filter value from the temporary tag
    TGp = DM.GetPersistentTagGroup()
    returnVal, val = TGp.GetTagAsText('DM2Python CV2')
    
    wsIDF = wsID
    #print("\n ReturnVal is "+str(returnVal))
    
    if (returnVal == 1):
        wsIDF = val
        #print(wsIDF)
        
    # And now remove the temporary tag
    DM.GetPersistentTagGroup().DeleteTagWithLabel("DM2Python CV2")
    
    #print("\n wsIDF is "+str(wsIDF))
        
    
    # Show as separate DM image
    DMImgC = DM.CreateImage(Conv.copy())
    del Conv    # Remove data from memory no longer needed
    DMImgC.SetName("Convolution " + dmImg.GetName())
    Calibration_Copy(dmImg, DMImgC)
    Tag_Copy(dmImg, DMImgC )#, 'Copied over' )
    TagProcessing(DMImgC, "convolution"+str(d))
    #print("convolution")
    DMImgC.ShowImage()
    try:
        CV2ImgMove(wsIDF)
    except:
        print("automated move to workspace error")
    
    
    DMImgBlu = DM.CreateImage(blur.copy())
    del blur    # Remove data from memory no longer needed
    DMImgBlu.SetName("Blur " + dmImg.GetName())
    Calibration_Copy(dmImg, DMImgBlu)
    Tag_Copy(dmImg, DMImgBlu )#, 'Copied over' )
    TagProcessing(DMImgBlu, "Blur"+str(d))
    DMImgBlu.ShowImage()
    try:
        CV2ImgMove(wsIDF)
    except:
        print("automated move to workspace error")
    
    
    DMImgMB = DM.CreateImage(median_blur.copy())
    del median_blur    # Remove data from memory no longer needed
    DMImgMB.SetName("Median Blur " + dmImg.GetName())
    Calibration_Copy(dmImg, DMImgMB)
    Tag_Copy(dmImg, DMImgMB )#, 'Copied over' )
    TagProcessing(DMImgMB, "Median blur"+str(d))
    DMImgMB.ShowImage()
    try:
        CV2ImgMove(wsIDF)
    except:
        print("automated move to workspace error")
    
    DMImgGaus = DM.CreateImage(Gaus.copy())
    del Gaus    # Remove data from memory no longer needed
    DMImgGaus.SetName("Gaussian " + dmImg.GetName())
    Calibration_Copy(dmImg, DMImgGaus)
    Tag_Copy(dmImg, DMImgGaus )#, 'Copied over' )
    TagProcessing(DMImgGaus, "Gaussian"+str(d))
    DMImgGaus.ShowImage()
    try:
        CV2ImgMove(wsIDF)
    except:
        print("automated move to workspace error")
    
    
    DMImgBil = DM.CreateImage(bil.copy())
    del bil    # Remove data from memory no longer needed
    DMImgBil.SetName("Bilateral " + dmImg.GetName())
    Calibration_Copy(dmImg, DMImgBil)
    Tag_Copy(dmImg, DMImgBil )#, 'Copied over' )
    TagProcessing(DMImgBil, "Bilateral"+str(d))
    DMImgBil.ShowImage()
    try:
        CV2ImgMove(wsIDF)
    except:
        print("automated move to workspace error")
        from time import sleep
        sleep(0.1)
        CV2ImgMove(wsIDF)
    
    
    #Show Wiener
    DMImgWien = DM.CreateImage(wien.copy())
    del wien    # Remove data from memory no longer needed
    DMImgWien.SetName("Wiener " + dmImg.GetName())
    Calibration_Copy(dmImg, DMImgWien)
    Tag_Copy(dmImg, DMImgWien )#, 'Copied over' )
    TagProcessing(DMImgWien, "Wiener"+str(d))
    DMImgWien.ShowImage()
    try:
        CV2ImgMove(wsIDF)
    except:
        print("automated move to workspace error")
    
    # Rearrange the filtered workspace so all images are visible
    dmscript = 'WorkspaceArrange('+str(wsIDF)+',1,1)'
    #print(dmscript)
    DM.ExecuteScriptString(dmscript)
    
    # now remove python variables, as they exist as images in GMS space now
    del DMImgC
    del DMImgBlu
    del DMImgMB
    del DMImgGaus
    del DMImgBil
    del DMImgWien
    
    dmImg.ShowImage()
    
# Define pixel diamater of filters
d_in = 15
bVal, d = DM.GetNumber( 'Pixel diameter of filter (odd integers only)?', d_in )  
d = int(d)
DoFilter(d)
DM.OkDialog("Filtered images in the workspace Filtered")
