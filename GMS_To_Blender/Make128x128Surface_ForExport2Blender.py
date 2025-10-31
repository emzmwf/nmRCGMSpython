# Get front dm image, extract square region
# and bin down to 128x128

import DigitalMicrograph as DM
import numpy as np


def DefineFolderLocation():
    globalTags = DM.GetPersistentTagGroup()
    folder = input( 'Please paste directory folder here FORWARD SLASHES:' )
    print( 'You have entered: ', folder )
    globalTags['DM2Blender Folder'] = folder
    return folder

def GetFolderLocation():
    globalTags = DM.GetPersistentTagGroup()
    try:
        folder = globalTags['DM2Blender Folder']
    except:
        print("Folder not defined")
        folder = DefineFolderLocation()
    return folder


def rebin(arr, new_shape):
    """Rebin 2D array arr to shape new_shape by averaging."""
    shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)

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
    

def makesurface(z):
    
    x = np.linspace(0,128, 128)
    y = np.linspace(0, 128, 128)
    x, y = np.meshgrid(x, y)
    print(x.shape)
    print(y.shape)
    print(z.shape)
    #print(GetFolderLocation())
    try:
        folder = str(GetFolderLocation())+'/NPArrays128.npz'
    except:
        print("Folder badly defined")
        folder = DefineFolderLocation()
        
    #folder = 'X:/MW Fay/Scripts/Image Processing/BlenderRender'+'/NPArrays128.npz'
    #print(folder)
    np.savez(folder,x,y,z)
   

makesurface(GetCrop())

#To do - add default directory save location checking instead of hard coded
