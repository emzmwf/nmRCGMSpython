## Plot crystal structure and diffraction pattern from cif file

# Requires py4DSTEM and pymatgen to be installed
# Recommend doing this from requirements.txt with fixed numpy == 1.23.5

from pymatgen.core.structure import Structure, Lattice
import py4DSTEM

import tkinter as tk
from tkinter import filedialog

def MakeBraggNumpy(bragg_np, arr):
    import math
    ptx = int((arr[0]+2)*100)
    pty = int((arr[1]+2)*100)
    vtemp = arr[2]
    val = vtemp*1000
    a = range(-5, 5, 1)
    b = range(-5, 5, 1)
    for c in a:
        for d in b:
            distance = math.sqrt((c)**2 + (d)**2)
            if distance <5:
                bragg_np[ptx+c, pty+d] = val
#

###############
#Main body#
###############
def MainBody():

    # use tkinter to open a file
    root = tk.Tk()
    root.withdraw()

    ftypes = (
        ('cif files', '*.cif'),
        ('text files', '*.txt')
        )

    file_cif = filedialog.askopenfilename(title="Select .CIF file", filetypes = ftypes)
    from pathlib import Path    
    fname = Path(file_cif).name



    ### CIF FILE
    crystal = py4DSTEM.process.diffraction.Crystal.from_CIF(file_cif)
    print("Enter HKL values and voltage in kV")

    ### HKL
    H = 1
    K = 1
    L = 1
    H = int(input("H: "))
    K = int(input("K: "))
    L = int(input("L: "))

    ##Voltage
    kV = 200
    kV = int(input("kV: "))

    # Calculate and plot the structure factors
    k_max = 2.0   # This is the maximum scattering vector included in the following calculations

    print("Calculating Diffraction")
    crystal.calculate_structure_factors(k_max)

    # specify the accelerating voltage
    crystal.setup_diffraction(kV*1000)

    zone_axis_test = [H, K, L]  # Zone axis

    bragg_peaks = crystal.generate_diffraction_pattern(
        zone_axis_lattice = zone_axis_test,
        sigma_excitation_error=0.02
    )

    #Note, need to identify how to set the title of these plots, it's not the same was as with matplotlib

    # bragg_peaks is a pointlist with 6 fields, qx, qy, intensity, h, k and l
    # to create a DM image for this, create an image with size range -k_max to +k_max, iterate over bragg_peaks to add each pixel value
    import numpy
    sz = int(k_max*2*100)
    bragg_np = numpy.zeros((sz,sz))

    for x in range(len(bragg_peaks)):
        MakeBraggNumpy(bragg_np, bragg_peaks[x])

    img = DM.CreateImage(bragg_np)
    img.SetName(str(fname)+"["+str(H)+"] ["+str(K)+"] ["+str(L)+"]")
    img.ShowImage()
    # set calibration - 
    #print(bragg_peaks[10])

    del img
#

MainBody()
