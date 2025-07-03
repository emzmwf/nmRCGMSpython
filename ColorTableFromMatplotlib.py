import matplotlib.pyplot as plt 
import DigitalMicrograph as DM
import numpy as np

style_list = ['default', 'classic'] + sorted(style for style in plt.style.available if style != 'classic')
print("\n")
print(style_list)

#cmapname = 'twilight'
#cmapname = 'twilight_shifted'
#cmapname = 'viridis'
#cmapname = 'hsv'
#cmapname = 'Spectral'
#cmapname = 'turbo'
#cmapname = 'plasma'
cmapname = 'PiYG'
cmap = plt.get_cmap(cmapname)

arr = np.arange(start=0, stop=256, step=1)

# 0 to 512 for twilight
#arr = np.arange(start=0, stop=512, step=2)


Barr = np.reshape(arr, (16, 16))

rgba_img = cmap(Barr)
#DM Python does not support RGB image creation yet

print(np.shape(rgba_img))

r = (rgba_img[:,:,0])
g = (rgba_img[:,:,1])
b = (rgba_img[:,:,2])

print(np.shape(r))
R = np.copy(r)
G = np.copy(g)
B = np.copy(b)

imgB = DM.CreateImage(B)
imgB.SetName('Blue')
imgB.ShowImage()

imgG = DM.CreateImage(G)
imgG.SetName('Green')
imgG.ShowImage()

imgR = DM.CreateImage(R)
imgR.SetName('Red')
imgR.ShowImage()

del rgba_img
del r
del g
del b


