import numpy as np
import DigitalMicrograph as DM

def create_annular_mask(shape, center, r_inner, r_outer):
    """
    Create a 2D boolean annular ring mask.
    shape: tuple of (height, width)
    center: tuple of (y, x) coordinates for the ring center
    r_inner: inner radius of the ring
    r_outer: outer radius of the ring
    """
    y, x = np.ogrid[:shape[0], :shape[1]]
    dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    
    # True for pixels inside the ring
    mask = (dist_from_center >= r_inner) & (dist_from_center <= r_outer)
    return mask

def ring_median(img, inrad, radwid):
    """
    Apply mask to increasing radius from image, get median value, return to array
    """
    outrad = inrad+radwid
    mask = create_annular_mask(
        img.shape, 
        (cy, cx),
        inrad,
        outrad
        )
    ring_pixels = img[mask]
    if ring_pixels.size ==0:
        return np.nan
    
    return np.median(ring_pixels)

image1 = DM.GetFrontImage()
img = np.abs(image1.GetNumArray())
imx, imy = img.shape

cx = imx//2	#floor division
cy = imy//2
#or get cx, cy from calibrations
radwid = 20
maxrad = min(cx, cy)

meds = []

for r in range(radwid, maxrad, 1):
    meds.append(ring_median(img, r, radwid))


medarr = np.array(meds, dtype='float32')
print(medarr)

DMplot =  DM.CreateImage(np.copy((medarr)))
DMplot.SetName("median profile of image")
DMplot.ShowImage()