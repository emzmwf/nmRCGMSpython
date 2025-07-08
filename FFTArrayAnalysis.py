import DigitalMicrograph as DM
import numpy as np
import sys
import time
from numpy.lib.stride_tricks import as_strided
import scipy

## Turn HRTEM image into FFT 4D Stack
## Using functions from Ben Miller (Gatan)

## TO DO - option for reduced area FFT instead? all useful data may be in centre of FFT

#User-Set Parameters XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#Set FFT Size and Spacing (Default 128,32) Smaller spacing will rapidly increase processing time and file size
FFTsize = 128
spacing = 32
bVal, FFTsize = DM.GetNumber( 'FFTsize', 128 ) 
cVal, spacing = DM.GetNumber( 'spacing', 32 ) 
FFTsize = int(FFTsize)
spacing = int(spacing)
#Set Percentage of Radial Profile (from center) to be Ignored (Default 10)
dVal, maskP = DM.GetNumber( 'mask percentage', 5 ) 
#Set the minimum distance between spots (to generate masked 4D dataset)
min_spot_dist = 5
#Set to number to also mask the center vertical and horizontal lines in the FFT, set to 0 to not mask (Default 2)
eVal, maskC_width = DM.GetNumber( 'vertical and horizontal mask width', 0 )
#Set memory usage level (GB) above which the code will ask user if they want to continue. (Default 6)
mem_warn_limit = 6
#Set whether to pad the result border so that the result image has the exact same shape as the input data (Default True)
pad_border = True
#Set the padding mode. Available options are given here: https://numpy.org/doc/stable/reference/generated/numpy.pad.html (Default 'constant')
pad_mode = 'constant'
#Set how much to bin the raw image data prior to computing FFTs higher values save time, but may result in loss of information (Default 1)
binning = 1
#Set whether to filter data prior to analysis (for FFTs this is a gaussian filter, and for 4D STEM a more computationally expensive median filter)
pre_filter = True

#Parameters for time series only
#(For a time-series of images) Set a single intensity scale maximum so that all colormaps in the series are scaled the same (Default None)
RGB_scale_max = None
#(For a time-series of images) Set which frame in the dataset is displayed as a datacube  (Default -1)
#Set this to -1 to not display a datacube
showdatacube_frame = -1
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


def strided_binning2D(array,binning=(1,1)):
	"""
	Function to Bin 2D Data 
	Accepts:
		array		2D numpy array to be binned
		binning		2 element tuple of integer binning amounts (bin_x, bin_y)
	Returns: A binned 2D array
	"""
	bin=np.flip(binning)
	nh = (array.shape[0]-bin[0])//bin[0]+1
	nw = (array.shape[1]-bin[1])//bin[1]+1
	strides = (array.strides[0],array.strides[1],array.strides[0]*bin[0],array.strides[1]*bin[1])
	strides = (array.strides[0],array.strides[1],array.strides[0]*bin[0],array.strides[1]*bin[1])
	shape = (bin[0],bin[1],nh,nw)
	virtual_datacube = as_strided(array,shape=shape,strides=strides)
	result = np.sum(virtual_datacube,axis=(0,1))
	return result
#



def mask_FFT_center(array,mask_percent,mask_cross_width):
	"""
	Function to mask diffractogram or diffraction-pattern central spot and cross lines
	Accepts:
		array				2D (or 4D) numpy array representing a single diffractogram/diffraction-pattern (or a 4D cube of them)
		mask_percent		number between 0 and 100 specifying the central circlular mask diameter as a percentage of the diffractogram/diffraction-pattern size 
		mask_cross_width	integer number specifying the number of pixels to mask (both vertically and horizontally) on either side of the pattern center 
	Returns:				a masked 2D (or 4D) numpy array representing a single diffractogram/diffraction-pattern (or a 4D cube of them)
	"""
	def create_circular_center_mask(r,FFT_size):
		r=int(r)
		size=2*r+1
		Y, X = np.ogrid[:size, :size]
		dist_from_center = np.sqrt((X - (r))**2 + (Y-(r))**2)
		image_mask = np.zeros((FFT_size,FFT_size))
		center = int(FFT_size//2)
		image_mask[center-r:center+r+1,center-r:center+r+1]=dist_from_center <= r
		return image_mask.astype('bool')
	
	m = mask_cross_width
	FFT_size = array.shape[-1]
	if len(array.shape)==4:
		maskval = np.median(np.min(array, axis=(0,1)))
		if mask_cross_width>0:
			array[:,:,FFT_size//2-m+1:FFT_size//2+m,:] = maskval
			array[:,:,:,FFT_size//2-m+1:FFT_size//2+m] = maskval
		if mask_percent>0:
			mask = create_circular_center_mask(mask_percent/100*FFT_size/2,FFT_size)
			array[:,:,mask] = maskval
		return array
	if len(array.shape)==2:
		maskval = np.percentile(array,1)
		if mask_cross_width>0:
			array[FFT_size//2-m+1:FFT_size//2+m,:] = maskval
			array[:,FFT_size//2-m+1:FFT_size//2+m] = maskval
		if mask_percent>0:
			mask = create_circular_center_mask(mask_percent/100*FFT_size/2,FFT_size)
			array[mask] = maskval
		return array
#




def FFT_Array_Analysis(imo,FFTsize,spacing,maskP,maskC_width,show_cube=False, data=None, smooth=True):
	"""
	Function (similar to STEMx_Array_Analysis) to process a 2D image by first splitting into many patches and computing FFTs,
		transforming it into a 4D data cube resembling a 4D STEM dataset
	Accepts:
		imo				2D DM image variable (not a numpy array)
		FFTsize			integer (preferably 2^n) specifying the pixel size of the FFTs to be computed  FFT.shape = (FFTsize,FFTsize)
		spacing			integer specifying the spacing between windows of data from which FFTs are computed. If FFTsize = spacing, then no overlap occurs. 
		maskP			number between 0 and 100 specifying the central circlular mask diameter as a percentage of the diffractogram/diffraction-pattern size 
		maskC_width		integer number specifying the number of pixels to mask (both vertically and horizontally) on either side of the pattern center 
		ShowCube		boolean specifying whether to display a masked,filtered FFT datacube in GMS 
		data			optional 2D numpy array that overrides the data in the required DM image variable (used to pass in data that has been processed rather than raw data)
		smooth			boolean specifying whether to process the data with a gaussian filter (to reduce spurious noise) prior to processing. this is recommended
	Returns:		
		r_max			2D numpy array where each pixel is the distance-from-center of the maximum pixel in each diffractogram
		t_max			2D numpy array where each pixel is the angle from the horizontal of the maximum pixel from each diffractogram
		i_max			2D numpy array where each pixel is the intensity of the maximum pixel from each diffractogram
		diff_max		2D numpy array giving a single diffractogram, where every pixel is the maximum value of that pixel across all diffractograms in the datacube
	"""
	#stime=time.perf_counter()
	time_it = 0
	if data is None: data = imo.GetNumArray()
	
	if(len(data.shape) != 2): 
		DM.OkDialog('Image is not 2D... aborting script')
		sys.exit()
	data = strided_binning2D(data, binning=(binning,binning))
	#Create 4D Diffractogram Datacube (Like 4D STEM datacube)
	(w0,h0) = data.shape
	nw = (w0-FFTsize)//spacing+1
	nh = (h0-FFTsize)//spacing+1

	#Create (Virtual) 4D Datacube of Image Regions 
	shape = (FFTsize,FFTsize,nw,nh)
	strides = (data.strides[0],data.strides[1],data.strides[0]*spacing,data.strides[1]*spacing)
	image_datacube = np.transpose(as_strided(data,shape=shape,strides=strides),(2,3,0,1))
	#Create Hanning Window
	hanningf = np.hanning(FFTsize)
	hanningWindow2d = np.sqrt(np.outer(hanningf, hanningf)).astype('float32')
	#Compute FFTs
	print("Computing %s FFTs..." %(nw*nh))
	start_timef=time.perf_counter()
	datacube = np.log(np.fft.fftshift(np.abs(np.fft.fft2(hanningWindow2d*image_datacube))**2, axes=(2,3))).astype('float32')
	print("FFT Computation Time: %s s" %(time.perf_counter()-start_timef))
	#if smooth: datacube = scipy.ndimage.median_filter(datacube, size=(1,1,3,3))
	if smooth: datacube = scipy.ndimage.gaussian_filter(datacube,sigma=(0,0,1,1),truncate=2)
	datacube = mask_FFT_center(datacube,maskP,maskC_width)
	
	if show_cube: 
		origin, x_scale, scale_unit =  imo.GetDimensionCalibration(1, 0)
		name = imo.GetName()
		def front_image_create_diff_picker_dm(t,l,b,r):
			fipdm = ('image Picker_Im = PickerCreate( GetFrontImage(), '+str(t)+','+str(l)+','+str(b)+','+str(r)+')')
			DM.ExecuteScriptString(fipdm)
		dc_im = DM.CreateImage(np.copy(datacube.astype('float32')))
		dc_im.SetDimensionCalibration(0,-1/(2*(x_scale*binning)),1/(x_scale*binning)/FFTsize,scale_unit+"-1",0)
		dc_im.SetDimensionCalibration(1,-1/(2*(x_scale*binning)),1/(x_scale*binning)/FFTsize,scale_unit+"-1",0)
		dc_im.SetDimensionCalibration(2,0,(x_scale*binning)*spacing,scale_unit,0)
		dc_im.SetDimensionCalibration(3,0,(x_scale*binning)*spacing,scale_unit,0)
		dc_im.SetName("4D_FFT Array of "+name)
		dc_im.GetTagGroup().SetTagAsBoolean('Meta Data:Data Order Swapped', True)
		dc_im.GetTagGroup().SetTagAsString('Meta Data:Format', 'Diffraction image')
		dc_im.GetTagGroup().SetTagAsString('Meta Data:Acquisition Mode', 'FFTs of TEM Image')
		dc_im.ShowImage()
		DM.ExecuteScriptString("GetFrontImage().setzoom("+str(3)+")\nImageDocumentOptimizeWindow(GetFrontImageDocument())")
		t=datacube.shape[0]//2-max(datacube.shape[0]//10,1)
		b=datacube.shape[0]//2+max(datacube.shape[0]//10,1)
		l=datacube.shape[1]//2-max(datacube.shape[1]//10,1)
		r=datacube.shape[1]//2+max(datacube.shape[1]//10,1)
		try: front_image_create_diff_picker_dm(t,l,b,r)
		except: print("Ignoring DM Error") 
		disp = dc_im.GetImageDisplay(0)
		del dc_im
	del imo
	#Find the maximum pixel of each FFT
	x_max = (np.argmax(np.max(datacube[:,:,0:FFTsize//2,:], axis=2),axis=2)-FFTsize//2).astype('int')
	y_max = -(np.argmax(np.max(datacube[:,:,0:FFTsize//2,:], axis=3),axis=2)-FFTsize//2).astype('int')
	r_max = np.hypot(x_max, y_max)/FFTsize
	#r_max = np.hypot(x_max, y_max)/(x_scale*binning)/FFTsize
	t_max = np.arctan2(y_max, x_max)/np.pi*180
	t_max[t_max<0] += 180
	i_max = np.max(datacube, axis=(2,3))
	#Also calculate a maximum diffractogram
	diff_max = np.max(datacube, axis=(0,1))
	if pad_border:
		padx = FFTsize//spacing//2
		pady = FFTsize//spacing//2
		r_max = np.pad(r_max,((padx, padx), (pady, pady)),mode=pad_mode, constant_values = np.min(r_max))
		t_max = np.pad(t_max,((padx, padx), (pady, pady)),mode=pad_mode, constant_values = np.min(t_max))
		i_max = np.pad(i_max,((padx, padx), (pady, pady)),mode=pad_mode, constant_values = np.min(i_max))
	
	return(r_max,t_max,i_max,diff_max)

def DoStuff():
    dmImg = DM.GetFrontImage() # Get reference to front most image
    
    r_max,t_max,i_max,diff_max = FFT_Array_Analysis(dmImg,FFTsize,spacing,maskP,maskC_width,show_cube=True, data=None, smooth=True)
    DM_RM = DM.CreateImage(r_max.copy())
    DM_RM.SetName("R max")
    DM_RM.ShowImage()
    DM_TM = DM.CreateImage(t_max.copy())
    DM_TM.SetName("T Max")
    DM_TM.ShowImage() #Could colour this one with a cyclic colormap
    DM_IM = DM.CreateImage(i_max.copy())
    DM_IM.SetName("I Max")
    DM_IM.ShowImage()
    DM_DiffM = DM.CreateImage(diff_max.copy())
    DM_DiffM.SetName("Diff Max")
    DM_DiffM.ShowImage()

print("\n \n \n HRTEM to FFT array \n ")

DoStuff()
