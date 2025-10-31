# Get front dm image, extract square region
# and bin down to 128x128
# MWF for UoN October 2025

import DigitalMicrograph as DM
import numpy as np

# Documentation for using the GMS UI from python is patchy
# so the alternative is to start using tkinter, or just ask for a 
# string and rely on the user realising we want forward slashes not back
def DefineFolderLocation():
    globalTags = DM.GetPersistentTagGroup()
    folder = input( 'Please paste directory folder here FORWARD SLASHES:' )
    print( 'You have entered: ', folder )
    globalTags['DM2Blender Folder'] = folder
    return folder

# See if the folder location is in global tags
def GetFolderLocation():
    globalTags = DM.GetPersistentTagGroup()
    try:
        folder = globalTags['DM2Blender Folder']
    except:
        print("Folder not defined")
        folder = DefineFolderLocation()
    return folder

# Rebin the image to the desired size
def rebin(arr, new_shape):
    """Rebin 2D array arr to shape new_shape by averaging."""
    shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)

# Get the front image or the crop within it
def GetCrop():
    dmImg = DM.GetFrontImage() # Get reference to front most image
    dmImgData = dmImg.GetNumArray() # Get NumpyArray to image data

    imshape = dmImgData.shape
    sqdim = min(imshape)
    newimg = dmImgData[0:sqdim,0:sqdim]
    outsize = 128
    print("\n binfactor "+str(outsize))
    binimg = rebin(newimg, (outsize,outsize))
    return binimg
    
#Convert the GMS data into a numpy array
def makesurface(z):
    
    x = np.linspace(0,128, 128)
    y = np.linspace(0, 128, 128)
    x, y = np.meshgrid(x, y)
    print(x.shape)
    print(y.shape)
    print(z.shape)
    try:
        folder = str(GetFolderLocation())+'/NPArrays128.npz'
    except:
        print("Folder badly defined")
        folder = DefineFolderLocation()
        
    np.savez(folder,x,y,z)
   

makesurface(GetCrop())

#To do - add default directory save location checking instead of hard coded
