## Python script to do something like a Zemin tableau
## Temporarily adjusts bright tilt around a centre to show distortions
## and shows modulus of FFTs arranged in a new workspace
## Checks if GMS has calibrated beam tilts
## Runs uncalibrated if not
## First version - MWF June 2024
## Display updating - MWF July 2024
###NOTE - display updating is still a bodge. 

import time
import DigitalMicrograph as DM
import numpy as np

## Define global variables
CalBT = 0
TX = 0
TY = 0
CropVal = 4

## Microscope control section to do the beam tilt / CLA2 / Bright Tilt
def DoBeamTilts():
    try:
        tiltX, tiltY = DM.Py_Microscope().GetCalibratedBeamTilt()
        print("calibrated beam tilt")
        print(tiltX, tiltY)
    except:
        print("Beam tilt not calibrated at this voltage")
    
    TX, TY = DM.Py_Microscope().GetBeamTilt()
    print("raw beam tilt")
    print(TX, TY)
    
    HTX = hex(int(TX))
    HTY = hex(int(TY))
    print("Hex beam tilt CLA2")
    print(HTX, HTY)
    return(TX,TY)
# End beam tilts DEF

# DEF to calculate and return the mod FFT of the input image
##ToDO - should we zoom in on this FFT? Think we should reduce this FFT
def DoModFFT(dmImg):
    dmImgData = dmImg.GetNumArray() # Get NumpyArray to image data
    nom = dmImg.GetName()
    ###Reduce to square region to avoid weirdness
    W = int(dmImg.GetImgWidth())
    H = int(dmImg.GetImgHeight())
    WS = int((W-H)/2)
    WE = WS+int(W/2)
    dmImgDataSq = dmImgData[0:H, WS:WS+H]
    out = np.fft.fftn(dmImgDataSq)
    outSH = np.fft.fftshift(out, axes=(0,1))
    #print("fft shape is")
    #print(outSH.shape)
    ### bin, resize, crop etc here
    ###center is half of size
    cx = round(W/2)
    cy = round(H/2)
    ###cropped pixel width
    cpwid = int(W/CropVal)
    cleft = round(cx - (cpwid/2))
    cright = round(cx + (cpwid/2))
    crop_A = outSH[cleft:cright, cleft:cright]
    ###
    #outA = DM.CreateImage(abs(outSH))
    outA = DM.CreateImage(abs(crop_A))
    outA.SetName('fft'+nom)
    origin, scale, unit =  dmImg.GetDimensionCalibration(0, 0)
    unitOut = str(unit)+str("-1")
    scaleOut = 1/(scale*H)
    origin =-(outA.GetImgWidth()/2)/(H*scale)
    outA.SetDimensionCalibration(0,origin,scaleOut,unitOut,0)
    outA.SetDimensionCalibration(1,origin,scaleOut,unitOut,0)    
    return(outA)
    #
#

#DEF to get current monitor resolution
def GetScreenSize():
    ## Really want to get the size of the View Window in GMS, but not worked that out, so just get monitor size
    import ctypes
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return(screensize)

### def to move front image doc to stated workspace
## NOTE - Sz does nothing at the moment, amend to position for more than one value
## e.g. Based on largest Sz value and size of screen (def GetScreenSize)
def ZemImgMove(wsOut, img, Tx, Ty, Sz):
    #imageDocA = DM.GetFrontImageDocument()
    ImageDocA = img.GetOrCreateImageDocument()
    ImageDocA.MoveToWorkspace(int(wsOut))
    docWinA = ImageDocA.GetWindow() 
    docWinA.SetFrameSize(100, 100)
    A = GetScreenSize() #Get the screen size
    d = min(A)  #Use the smaller axis to determine distances
    
    #Tx and Ty are proportional to Sz range -1 to 1, so use that to decide positions
    XM = Tx/Sz
    YM = Ty/Sz
    xms = str(round(XM,2))
    yms = str(round(YM,2))
    print(xms+" "+yms)
    
    #get W and H of img 
    FiddleFactor = 10    # 5 for K3 2kx2k, 10 for OneView
    #Check what camera we are on for fiddle factor. 
    #Decrease the factor if the images are too close, overlapping
    # Set for TEM based on camera - for UoN where OneView is on 2100Plus, K3 on 2100F
    camera = DM.GetActiveCamera()
    if (camera.GetName() == 'OneView'):
        FiddleFactor = 8
    if (camera.GetName() == 'K3'):
        FiddleFactor = 5
    W = int(img.GetImgWidth())
    H = int(img.GetImgHeight())
    XD = CropVal*int(W/FiddleFactor)*XM+(d*0.4)#Slightly under half to allow for menu and output viewer
    YD = CropVal*int(H/FiddleFactor)*YM+(d*0.4)

    # 200 is ok for 8, try 100 for 12-16
    ImSz = 100
    ImageDocA.ShowAtRect(int(YD-ImSz), int(XD-ImSz), int(YD+ImSz), int(XD+ImSz))
    

##Def to calculate calibrated x and y shifts, given current count, total count and difference amount
def CalcTXTY(cNo, tNo, Diff):
    import math
    pi = math.pi
    n = tNo
    r = Diff
    TX = math.cos(2*pi/n*cNo)*r
    TY = math.sin(2*pi/n*cNo)*r
    return(TX, TY)
#end of def


#def to change CLA2 (Bright Tilt DEF adjust)
def DoZemlin(BTAmount):
    camera = DM.GetActiveCamera()
    camera.PrepareForAcquire()
    parameters = camera.GetDefaultParameters()
    print(parameters)
    try:
        tiltX, tiltY = DM.Py_Microscope().GetCalibratedBeamTilt()
        CalBT = 1
    except:
        print("Beam tilt not calibrated")
        print("Using uncalibrated raw values")
        print("And default raw adjust of 250")
        tiltX, tiltY = DM.Py_Microscope().GetBeamTilt()
        BTAmount = 250
        CalBT = 0

    # Get workspace ready - unclear what Python command is still!
    #So hybrid it
    dmscript = 'number wsID_src = WorkSpaceGetActive()' + '\n'
    dmscript += 'number wsID_Zem = WorkSpaceAdd( WorkSpaceGetIndex(wsID_src) + 1 )' + '\n'
    dmscript += 'WorkspaceSetName( wsID_Zem , "Zemlin" )' + '\n'
    dmscript += 'TagGroup tg = GetPersistentTagGroup( ) ' + '\n'
    dmscript += 'tg.TagGroupSetTagAsString( "DM2Python CV2", ""+wsID_Zem )' + '\n'

    DM.ExecuteScriptString( dmscript ) 
    # Now get the wsID_Filter value from the temporary tag
    TGp = DM.GetPersistentTagGroup()
    returnVal, val = TGp.GetTagAsText('DM2Python CV2')
    if (returnVal == 1):
        wsIDF = val
    #end if loop
    DM.GetPersistentTagGroup().DeleteTagWithLabel("DM2Python CV2")
    
    
    #Total number of images in loop
    Tno = 12
    for i in range (0,Tno):
        Xdiff, Ydiff = CalcTXTY(i, Tno, BTAmount)
        # If calibrated, BTAmount could be 0.01, if uncalibrated it's 1000
        BtiltX = tiltX+Xdiff
        BtiltY = tiltY+Ydiff
        try:
            DM.Py_Microscope().SetCalibratedBeamTilt(BtiltX, BtiltY)
        except:
            DM.Py_Microscope().SetBeamTilt(BtiltX, BtiltY)
        time. sleep(0.25)
        xnom = str(round(BtiltX, 2))
        ynom = str(round(BtiltY, 2))
        iname = xnom+" "+ynom
        img = camera.AcquireImage()
        img.SetName(iname)
        modFFT = DoModFFT(img)
        modFFT.ShowImage() 
        ZemImgMove(wsIDF, modFFT, Xdiff, Ydiff, BTAmount)
        time. sleep(0.125)
        
    try:
        DM.Py_Microscope().SetCalibratedBeamTilt(tiltX, tiltY)
    except:
        DM.Py_Microscope().SetBeamTilt(tiltX, tiltY)
    iname = str(round(tiltX,2))+" "+str(round(tiltY,2))
    img = camera.AcquireImage()
    img.SetName(iname)
    modFFT = DoModFFT(img)  
    modFFT.ShowImage() 
    # check how to default show as high contrast for recent GMS
    ZemImgMove(wsIDF, modFFT, 0, 0, BTAmount)
    time. sleep(1)

# end DoZemlin def


print("\n========================")
print("Beam tilts initial state")
TX,TY = DoBeamTilts()
#BeamTiltAmount = 0.04 #40mrad
BeamTiltAmount = 0.08 #80mrad
###
# This will be adjusting CLA2
# Calibrated units are given in calibrated units according to the stored calibration - normally with Gatan this is rad (not mrad)
# suggest values:
# 80kV Plus @x250K 0.01 (10 mrad)
# 200kV Plus @ 100k 0.08 (80mrad)
# 200kV 2100F @50k with 1/2 frame 0.04 (40mrad)
# 200kV 2100F @150k with 1/2 frame 0.08 (80mrad)

#check if beam is blanked and warn if so
GetBeamBlanked = DM.Py_Microscope().GetBeamBlanked() 
if (DM.Py_Microscope().GetBeamBlanked()==1):
    DM.OkDialog('Beam is blanked! unblank before continuing')

# Should do some catch part here to put the tilts back if there's an error. This might work. 
try:
    DoZemlin(BeamTiltAmount)
except:
    #Put the tilts back
    DM.Py_Microscope().SetBeamTilt(TX, TY)

print("Beam tilts final state")
DoBeamTilts()

print("End of script")
DM.Py_Microscope().SetBeamBlanked(True)  
DM.OkDialog('Diffractogram tableau shown in workspace Zemlin')
