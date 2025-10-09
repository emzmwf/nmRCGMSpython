
import numpy as np
import DigitalMicrograph as DM

# LMx80 positions UoN 2100Plus
arr = np.array([[-699.525,-53.332],
 [-539.559,349.468],
 [-339.808,809.839],
 [123.356,593.238],

 [-55.2453,124.406],

 [-271.725,-301.564],

 [-517.22,-745.847],

 [191.516,-655.31],

 [425.842,-173.288],

 [640.593,280.861]
 ])

# Array of names if we want to name by relative position
arrnames = ("-1_-1_",
 "-1_0_",
 "-1_1_",
 "0_1_",
 "0_0_",
 "0_1_",
 "0_2_",
 "1_-1_",
 "1_0_",
 "1_1_")
# Either measure for each microscope, or add script to access
# Gatan calibrations to calculate positions

#Capture routine
def GetImage():
    exposure = 0.1
    bin = 1
    kUnproc = DM.GetCameraUnprocessedEnum()
    cam.AcquireImage( exposure, bin, bin).ShowImage()

'''
img2 = camera.CreateImageForAcquire( 2, 2 )  
 img2.ShowImage()  
 camera.AcquireInPlace( img2, 0.5, 2, 2, 1, 0, 0, 4096, 4096)  
 img2.UpdateImage()  
'''

stx = arr[0][0]
sty = arr[0][1]
print(stx)
print(sty)

len = np.shape(arr)[0]

#Ask user to put largest condensor aperture in
DM.OkDialog( 'Please ensure largest condensor aperture is used' )  

#Prepare microscope
DM.Py_Microscope().SetBeamBlanked(True)
DM.Py_Microscope().SetScreenPosition(2)
DM.Py_Microscope().SetImagingOpticsMode("LowMAG")
DM.Py_Microscope().SetMagIndex(2) 
DM.Py_Microscope().SetSpotSize(4) 
#DM.SetSpotSize(4)
DM.Py_Microscope().SetBrightness(63479)
DM.Py_Microscope().SetProjectorShift(30328, 31120)  
#PLA 30328 31120

cam = DM.GetActiveCamera()
cam.PrepareForAcquire()
cam.SetInserted( True ) # ensure camera is inserted

#Ask user to put largest condensor aperture in
DM.OkDialog( 'Ready to start acquisition' )  

# dm script for new workspace
dmScript = 'number wsID_src = WorkSpaceGetActive()' + '\n'
dmScript += 'number wsID_montage = WorkSpaceAdd( WorkSpaceGetIndex(wsID_src) + 1 )' + '\n'
dmScript += 'WorkSpaceSetActive( wsID_montage )' + '\n'
dmScript += 'WorkspaceSetName( wsID_montage , "LMMontage" )' + '\n'
# Execute DM script
DM.ExecuteScriptString( dmScript )


for i in range(len):
    stx = arr[i][0]
    sty = arr[i][1]
    print(stx)
    print(sty)
    #Move stage
    DM.Py_Microscope().SetBeamBlanked(True) 
    DM.Py_Microscope().SetStageX(stx)
    DM.Py_Microscope().SetStageY(sty)
    DM.OkDialog( 'press OK to continue \n when stage has stopped' )  
    #Wait
    DM.Py_Microscope().SetBeamBlanked(False) 
    GetImage()
    ImageFront = DM.GetFrontImage()
    # Naming - either from stage position, or relative integers?
    ImageFront.SetName("LMAG x:"+str(stx)+" y:"+str(sty))
    ImageFront.UpdateImage()
    
    #Wait
    

# blank beam
DM.Py_Microscope().SetBeamBlanked(True)

del ImageFront

# Auto-arrange window?  3,3,3,1 array?
# reset stage position?

#inform operator script has completed
DM.OkDialog( 'Script has completed' )  


