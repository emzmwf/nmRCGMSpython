### Imports
import numpy as np

if not DM.IsScriptOnMainThread(): print('Scipy scripts cannot be run on Background Thread.'); exit()
import scipy
from scipy import ndimage
from scipy import signal
from scipy import fftpack
from scipy.ndimage import geometric_transform

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
median = 0 #set to 1 to apply median filter to the FFT prior to profile creation (slows calculation, especially for large input images)
initial_result_image_width = 200 #how many profiles can be displayed in the intial result window (window is automatically expanded as needed)
profile_result_length_ratio = 2 #Set to some integer 2^N, N=>0. Smaller N will make calculation slower. Default: 4
profile_angular_sampling_resolution = 256 #set how many samples are taken around the circumference of the radial profile
print_timing = True      # (Default True) Select whether to output the time it takes to compute each frame
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

def topolar(img,  r_size, theta_size, order=1):
    sx, sy = img.shape
    max_radius = int(sx/2)
    #define transform
    def transform(coords):
        theta = 2.0*np.pi*coords[1] / (theta_size - 1.)
        radius = max_radius * coords[0] / r_size
        i = int(sx/2) - radius*np.sin(theta)
        j = radius*np.cos(theta) + int(sx/2)
        return i,j
    #perform transform
    polar = geometric_transform(img, transform, output_shape=(r_size,theta_size), order=order,mode='constant',cval=1.0,prefilter=False)    
    return polar


def FFT_radial_profile(image_o, profile_ang_res,length_ratio,do_median):    
    #compute FFT
    fft_im = np.absolute(scipy.fftpack.fftshift(np.fft.fft2(image_o)))
    #Median-Filter FFT to remove single-pixel outliers
    if do_median: fft_im_median = scipy.ndimage.median_filter(fft_im, size=3)
    else: fft_im_median = fft_im
    #determine profile size
    sx, sy = fft_im.shape
    profile_size = int(sx/length_ratio)
    #convert FFT image to polar coordinates
    polar_im = topolar(fft_im_median, profile_size, profile_ang_res, order=1)
    #compute radial mean and maximum profiles
    radial_max=np.amax(polar_im,1)
    radial_mean=np.mean(polar_im,1)
    #median-filter the radial mean profile to smooth this further
    radial_mean_median = scipy.signal.medfilt(radial_mean)
    #radial profile is radial-max minus radial-mean
    radial_profile = np.atleast_2d(radial_max-radial_mean_median)    
    return radial_profile
    


img1 = DM.GetFrontImage()
imageDoc = DM.GetFrontImageDocument()
imDocWin = imageDoc.GetWindow()
imageDisplay = img1.GetImageDisplay(0)

data = img1.GetNumArray()

profout = FFT_radial_profile(data,profile_angular_sampling_resolution,profile_result_length_ratio, median)
DMplot =  DM.CreateImage(np.copy((profout)))
DMplot.SetName("Radial profile of FFT")
DMplot.ShowImage()

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

print (np.shape(profout))
print(np.shape(profout)[1])

dt = 0.01
t = range(np.shape(profout)[1])
s = profout[0]
print(len(t))
print(len(s))

fig, (ax0, ax1) = plt.subplots(2, 1, layout='constrained')
ax0.plot(t, s)
ax0.set_xlabel('Spatial')
ax0.set_ylabel('Int')
ax1.psd(s, NFFT=512, Fs=1 / dt)
ax1.set_ylabel('Power Spectral Density')

plt.show()



print("fin")