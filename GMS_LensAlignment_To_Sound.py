import numpy as np
import scipy.io.wavfile as wav

def CreateInstrument(frequencies, amplitudes, sample_rate):
# Define the audio parameters
    duration = 2  # Duration in seconds
    # Generate the time axis
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Generate the audio signal
    audio_signal = np.zeros_like(t)
    # Add multiple sine waves to create a complex audio signal
    #frequencies = [440, 880, 1320]
    
    for frequency, amplitude in zip(frequencies, amplitudes):
        audio_signal += amplitude * np.sin(2 * np.pi * frequency * t)
    # Scale the audio signal to the appropriate range
    audio_signal *= 32767 / np.max(np.abs(audio_signal))
    
    #Hanning window
    print(audio_signal.shape)
    print(len(audio_signal))
    han = np.hanning(len(audio_signal))
    audio_signal = audio_signal * han
    return audio_signal

violin = [196, 293.7, 440,659.3]#violin 
pianoFACG = [65.406,110, 261.6256, 391.9954]# Piano FACG 
cello = [65.41,130.8,261.6,523.3]#Cello - condensers CL1, CL2, CL3, CM
'''
# 2100F STEM
CL = [65535, 0, 31570, 0]
OL = [46918, 33797,16428, 0]
IL = [21488, 46848, 32512, 64000]

# 2100F 250kx TEM
CL = [32976, 0, 37727, 31824]
OL = [47104, 35064, 0, 0]
IL = [41536, 39072, 21360, 64000]
'''

FImage = DM.FindFrontImage()
name = FImage.GetName()
tgs = FImage.GetTagGroup()
ldict = tgs['Microscope Info']['JEOL']['Lenses']
CL = [int(ldict['CL1']),int(ldict['CL2']),int(ldict['CL3']),int(ldict['CM'])]
OL = [int(ldict['OL Coarse']),int(ldict['OL Fine']),int(ldict['OL Super Fine']),int(ldict['OM1'])]
IL = [int(ldict['IL1']),int(ldict['IL2']),int(ldict['IL3']),int(ldict['PL1'])]

      
#Vio_amplitudes = [0.3, 0.2, 0.1, 0.1]# From - OLC, OLF, OLSF, OM
#Piano_amplitudes = [0.3, 0.2, 0.1, 0.1]# From IL1, IL2, IL3, PL1
#Cello_amp = [0.3, 0.2, 0.1, 0.4] # From CL1, CL2, CL3

Vio_amplitudes = np.divide(CL, 65535)
Piano_amplitudes = np.divide(OL, 65535)
Cello_amp = np.divide(IL, 65535)

sample_rate = 44100  # Sample rate in Hz
sr = sample_rate
Part_audio_signal = np.append(
    CreateInstrument(violin, Vio_amplitudes,sr),
    CreateInstrument(pianoFACG, Piano_amplitudes,sr),
    )

Fin_audio_signal = np.append(Part_audio_signal, CreateInstrument(cello, Cello_amp,sr))

# Convert the audio signal to the appropriate data type
Fin_audio_signal = Fin_audio_signal.astype(np.int16)
# Save the audio signal to a WAV file
#wav.write("C:/Users/VALUEDGATANCUSTOMER/Music/output"+str(name)+"_cfg.wav", sample_rate, Fin_audio_signal)

#tagPath = 'Private:Python:Python Path'
#globalTags = DM.GetPersistentTagGroup()
#destpath = (globalTags['Private']['Current Directory'])

import os
fpath = os.environ['USERPROFILE']

destpath = fpath+"/Documents"
wav.write(destpath+"/output"+str(name)+"_cfg.wav", sample_rate, Fin_audio_signal)


import sys
#np.set_printoptions(threshold=sys.maxsize)
#print(audio_signal)
print(" wav output to users Documents folder")