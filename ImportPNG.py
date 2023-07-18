# Import png image into GMS
# note, will do odd things to jpgs, which GMS supports directly loading anyway

import DigitalMicrograph as DM
import numpy
from PIL import Image


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
    #To display as mono
    R = nimg[:,:,0]
    G = nimg[:,:,1]
    B = nimg[:,:,2]
    Mono = 0.2989*R + 0.5870*G + 0.1140*B 
    DMmono= DM.CreateImage( Mono )
    DMmono.SetName(tail+"mono")
    DMmono.ShowImage()
    #Display as stack
    nimg = numpy.swapaxes(nimg, 0, 2)
    nimg = numpy.flip(nimg, 1)  # flip around axis
    nimg = numpy.rot90(nimg, k=3, axes=(1, 2))
    DMImg = DM.CreateImage(nimg.copy())
    DMImg.SetName(tail)
    DMImg.ShowImage()

