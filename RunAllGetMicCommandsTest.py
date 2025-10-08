import DigitalMicrograph as DM

 

mic = DM.Py_Microscope()

 

# Ouptut some microscope parameters

print( 'Brightness:', mic.GetBrightness() ) 

print( 'Focus:', mic.GetFocus() ) 

print( 'Condenser aperture:', mic.GetCondenserAperture() )


AllMics = [mic.GetBeamBlanked,
mic.GetBeamShift,
mic.GetBeamTilt,
mic.GetBrightness,
mic.GetCalibratedBeamShift,
mic.GetCalibratedBeamTilt,
mic.GetCalibratedCondenserStigmation,
mic.GetCalibratedFocus,
mic.GetCalibratedImageShift,
mic.GetCalibratedObjectiveStigmation,
mic.GetCalibrationStateTags,
mic.GetCameraLength,
mic.GetColumnValvesOpen,
mic.GetCondenserAperture,
mic.GetCondenserStigmation,
mic.GetFocus,
mic.GetHighTension,
mic.GetIlluminationMode,
mic.GetIlluminationModes,
mic.GetIlluminationSubMode,
mic.GetImageShift,
mic.GetImagingOpticsMode,
mic.GetImagingOpticsModes,
mic.GetMagIndex,
mic.GetMagnification,
mic.GetMicroscopeName,
mic.GetNumberOfCondenserApertures,
mic.GetNumberOfObjectiveApertures,
mic.GetObjectiveAperture,
mic.GetObjectiveStigmation,
mic.GetOperationMode,
mic.GetProjectorShift,
mic.GetScreenPosition,
mic.GetSpotSize,
mic.GetStageAlpha,
mic.GetStageBeta,
mic.GetStageX,
mic.GetStageXY,
mic.GetStageY,
mic.GetStageZ,
]

MicsNames = [
"GetBeamBlanked",
"GetBeamShift",
"GetBeamTilt",
"GetBrightness",
"GetCalibratedBeamShift",
"GetCalibratedBeamTilt",
"GetCalibratedCondenserStigmation",
"GetCalibratedFocus",
"GetCalibratedImageShift",
"GetCalibratedObjectiveStigmation",
"GetCalibrationStateTags",
"GetCameraLength",
"GetColumnValvesOpen",
"GetCondenserAperture",
"GetCondenserStigmation",
"GetFocus",
"GetHighTension",
"GetIlluminationMode",
"GetIlluminationModes",
"GetIlluminationSubMode",
"GetImageShift",
"GetImagingOpticsMode",
"GetImagingOpticsModes",
"GetMagIndex",
"GetMagnification",
"GetMicroscopeName",
"GetNumberOfCondenserApertures",
"GetNumberOfObjectiveApertures",
"GetObjectiveAperture",
"GetObjectiveStigmation",
"GetOperationMode",
"GetProjectorShift",
"GetScreenPosition",
"GetSpotSize",
"GetStageAlpha",
"GetStageBeta",
"GetStageX",
"GetStageXY",
"GetStageY",
"GetStageZ",
]


for op in AllMics:
    try:
        print(op)
        print(op())
        #print(MicsNames[op])
    except:
        print("value does not exist")

