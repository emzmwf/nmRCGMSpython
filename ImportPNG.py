# Import png image into GMS
# note, will do odd things to jpgs, which GMS supports directly loading anyway

import DigitalMicrograph as DM
import numpy
from PIL import Image

## Additional requirements above base GMS: 
# PIL

# RGB handling methods:
def AsMono(nimg, tail):
        R = nimg[:,:,0]
        G = nimg[:,:,1]
        B = nimg[:,:,2]
        Mono = 0.2989*R + 0.5870*G + 0.1140*B 
        DMmono= DM.CreateImage( Mono )
        DMmono.SetName(tail+"mono")
        DMmono.ShowImage()

def AsStack(nimg, tail):
        nimg = numpy.swapaxes(nimg, 0, 2)
        nimg = numpy.flip(nimg, 1)  # flip around axis
        nimg = numpy.rot90(nimg, k=3, axes=(1, 2))
        DMImg = DM.CreateImage(nimg.copy())
        DMImg.SetName(tail)
        DMImg.ShowImage()

def AsRGB(nimg, tail):
        # Build DM-script to create RGB image
        R = nimg[:,:,0]
        G = nimg[:,:,1]
        B = nimg[:,:,2]
        DMImgR = DM.CreateImage(R.copy())
        DMImgG = DM.CreateImage(G.copy())
        DMImgB = DM.CreateImage(B.copy())
        DMScriptRGB = '// This is a DM script' + '\n'
        DMScriptRGB += 'RGBImage col := RGB('
        DMScriptRGB += DMImgR.GetLabel() + ','
        DMScriptRGB += DMImgG.GetLabel() + ','
        DMScriptRGB += DMImgB.GetLabel() + ')' + '\n'
        DMScriptRGB += 'col.ShowImage()'
        
        # Run the DM script
        DM.ExecuteScriptString( DMScriptRGB )
        colimg = DM.GetFrontImage()
        colimg.SetName(tail)
        

def GetPng():


    #DM Script to return file path
    dmScript = 'string path = GetApplicationDirectory("open_save",0)' + '\n'
    dmScript += 'if (!OpenDialog(NULL,"Select png file",path, path)) exit(0)' + '\n'
    dmScript += 'TagGroup tg = GetPersistentTagGroup( ) ' + '\n'
    dmScript += 'tg.TagGroupSetTagAsString( "DM2Python String", path )' + '\n'

    # Execute DM script
    DM.ExecuteScriptString( dmScript )

    #Get the selection data into python
    TGp = DM.GetPersistentTagGroup()
    returnVal, path = TGp.GetTagAsText('DM2Python String')

    print(returnVal)
    print(path)

    import ntpath
    tail = ntpath.basename(path)
    print(tail)

    img = Image.open(path)
    nimg = numpy.array(img)
    print(nimg.shape)
    lnimg = len(nimg.shape)
    # if len is 2, can simply copy and show
    
    if lnimg == 2:
        DMImg = DM.CreateImage(nimg.copy())
        DMImg.SetName(tail)
        DMImg.ShowImage()
        # With colour rgb files, len will be three, so need more work
    else:
        print("colour stack identified")
        # DM Python does not support RGB image creation yet
        #To display as mono
        #AsMono(nimg, tail)
        #Display as stack
        #AsStack(nimg, tail)
        # Display as RGB
        AsRGB(nimg, tail)
       
GetPng()
